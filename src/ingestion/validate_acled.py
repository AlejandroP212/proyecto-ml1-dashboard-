"""Validate a small ACLED sample for Phase 2.

This script mirrors the lightweight validation approach used for GDELT:
- load credentials from .env when available;
- try ACLED's current OAuth flow first;
- fall back to legacy email/key access if credentials suggest that workflow;
- fetch a small, project-relevant sample;
- write a short Markdown summary for Phase 2.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # Keep validation usable even before dependencies are installed.
    load_dotenv = None


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
TABLES_DIR = ROOT / "reports" / "tables"

TOKEN_URL = "https://acleddata.com/oauth/token"
API_URL = "https://acleddata.com/api/acled/read"

SAMPLE_PARAMS = {
    "_format": "json",
    "country": (
        "Iran:OR:country=Israel:OR:country=Iraq:OR:country=Syria:OR:country=Lebanon"
        ":OR:country=Yemen"
    ),
    "event_date": "2026-05-01|2026-05-08",
    "event_date_where": "BETWEEN",
    "fields": (
        "event_id_cnty|event_date|country|admin1|location|event_type|sub_event_type|"
        "actor1|actor2|fatalities|latitude|longitude|source|notes"
    ),
    "limit": 100,
}


def load_credentials() -> dict[str, str]:
    if load_dotenv is not None:
        load_dotenv(ROOT / ".env")
    else:
        env_path = ROOT / ".env"
        if env_path.exists():
            for raw_line in env_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
    return {
        "email": os.getenv("ACLED_EMAIL", "").strip(),
        "password": os.getenv("ACLED_PASSWORD", "").strip(),
        "key": os.getenv("ACLED_KEY", "").strip(),
    }


def request_oauth_token(email: str, password: str) -> dict[str, Any]:
    response = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "username": email,
            "password": password,
            "grant_type": "password",
            "client_id": "acled",
            "scope": "authenticated",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if "access_token" not in payload:
        raise ValueError("OAuth response did not include access_token")
    return payload


def fetch_sample_with_oauth(email: str, password: str) -> dict[str, Any]:
    token_payload = request_oauth_token(email, password)
    response = requests.get(
        API_URL,
        params=SAMPLE_PARAMS,
        headers={
            "Authorization": f"Bearer {token_payload['access_token']}",
            "Content-Type": "application/json",
        },
        timeout=60,
    )
    response.raise_for_status()
    return {
        "auth_method": "oauth_password",
        "token_payload": token_payload,
        "response": response.json(),
        "request_url": response.url,
    }


def fetch_sample_with_legacy_key(email: str, key: str) -> dict[str, Any]:
    params = {
        **SAMPLE_PARAMS,
        "email": email,
        "key": key,
    }
    response = requests.get(API_URL, params=params, timeout=60)
    response.raise_for_status()
    return {
        "auth_method": "legacy_email_key",
        "response": response.json(),
        "request_url": response.url,
    }


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    countries: dict[str, int] = {}
    event_types: dict[str, int] = {}
    sub_event_types: dict[str, int] = {}
    total_fatalities = 0
    non_null_coordinates = 0

    for row in records:
        country = str(row.get("country", "") or "").strip()
        event_type = str(row.get("event_type", "") or "").strip()
        sub_event_type = str(row.get("sub_event_type", "") or "").strip()
        fatalities = row.get("fatalities")

        if country:
            countries[country] = countries.get(country, 0) + 1
        if event_type:
            event_types[event_type] = event_types.get(event_type, 0) + 1
        if sub_event_type:
            sub_event_types[sub_event_type] = sub_event_types.get(sub_event_type, 0) + 1
        if fatalities not in (None, ""):
            try:
                total_fatalities += int(fatalities)
            except (TypeError, ValueError):
                pass
        if row.get("latitude") not in (None, "") and row.get("longitude") not in (None, ""):
            non_null_coordinates += 1

    return {
        "row_count": len(records),
        "country_counts": dict(sorted(countries.items())),
        "event_type_counts": dict(sorted(event_types.items())),
        "sub_event_type_counts": dict(sorted(sub_event_types.items())),
        "total_fatalities": total_fatalities,
        "rows_with_coordinates": non_null_coordinates,
        "sample_rows": records[:5],
    }


def normalize_response(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("response", {})
    records = raw.get("data", []) if isinstance(raw, dict) else []
    summary = summarize_records(records if isinstance(records, list) else [])
    return {
        "auth_method": payload["auth_method"],
        "request_url": payload["request_url"],
        "status": raw.get("status"),
        "success": raw.get("success"),
        "message": raw.get("message"),
        "count": raw.get("count"),
        "summary": summary,
        "raw": raw,
    }


def write_summary(result: dict[str, Any]) -> Path:
    lines = [
        "# ACLED validation summary",
        "",
        f"Generated at: {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
        "## Validation status",
        "",
        f"- Outcome: {result['outcome']}",
        f"- Auth method attempted: {result.get('auth_method', 'none')}",
        f"- Request URL: {result.get('request_url', 'N/A')}",
        f"- Error: {result.get('error', 'None')}",
        "",
        "## Sample scope",
        "",
        "- Countries: Iran, Israel, Iraq, Syria, Lebanon, Yemen",
        "- Date range: 2026-05-01 to 2026-05-08",
        "- Limit: 100 rows",
        "",
    ]

    if result.get("summary"):
        summary = result["summary"]
        lines.extend(
            [
                "## Observed sample",
                "",
                f"- Rows returned: {summary['row_count']}",
                f"- API count field: {result.get('count', 'N/A')}",
                f"- Rows with coordinates: {summary['rows_with_coordinates']}",
                f"- Total fatalities in sample: {summary['total_fatalities']}",
                f"- Countries observed: {json.dumps(summary['country_counts'], ensure_ascii=False)}",
                f"- Event types observed: {json.dumps(summary['event_type_counts'], ensure_ascii=False)}",
                (
                    "- Sub-event types observed: "
                    f"{json.dumps(summary['sub_event_type_counts'], ensure_ascii=False)}"
                ),
                "",
                "## Decision hint",
                "",
                (
                    "- If this sample is complete and fields stay consistent, ACLED is a strong "
                    "candidate for the structured source and for target construction."
                ),
            ]
        )
    else:
        lines.extend(
            [
                "## Decision hint",
                "",
                (
                    "- Validation is blocked until ACLED credentials are available or one supported "
                    "authentication method succeeds."
                ),
            ]
        )

    output = TABLES_DIR / "acled_validation_summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    credentials = load_credentials()
    result: dict[str, Any] = {
        "outcome": "blocked",
        "auth_method": "none",
        "request_url": "N/A",
        "error": None,
        "summary": None,
    }

    try:
        if credentials["email"] and credentials["password"]:
            normalized = normalize_response(
                fetch_sample_with_oauth(credentials["email"], credentials["password"])
            )
            result.update({"outcome": "success", **normalized})
        elif credentials["email"] and credentials["key"]:
            normalized = normalize_response(
                fetch_sample_with_legacy_key(credentials["email"], credentials["key"])
            )
            result.update({"outcome": "success", **normalized})
        else:
            result["error"] = (
                "Missing ACLED credentials. Provide ACLED_EMAIL plus ACLED_PASSWORD "
                "(preferred) or ACLED_KEY (legacy fallback) in .env."
            )
    except Exception as exc:  # Validation should record failures instead of hiding them.
        result["error"] = f"{type(exc).__name__}: {exc}"

    raw_output = RAW_DIR / "acled_validation_sample.json"
    raw_output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    summary_path = write_summary(result)
    print(f"Wrote validation summary: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

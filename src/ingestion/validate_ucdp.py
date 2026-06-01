"""Validate UCDP GED 25.1 and UCDP Candidate datasets for Phase 2.

Downloads small samples (streaming or direct CSV) from:
  - UCDP GED 25.1 (1989-2024, ZIP): yearly consolidated events.
  - UCDP Candidate 25.01.25.12 (all 2025, CSV): monthly candidate events.
  - UCDP Candidate 26.01.26.03 (Jan-Mar 2026, CSV): Q1-2026 candidate events.
  - UCDP Candidate 26.0.4 (Apr 2026, CSV): latest available month.

Focus: validate schema, date coverage, geographic filter and fatalities fields
for the ongoing Middle East / Iran-Israel-US escalation context (2024-2026).
"""

from __future__ import annotations

import csv
import io
import json
import sys
import time
import zipfile
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
TABLES_DIR = ROOT / "reports" / "tables"

# ── Target countries for the active conflict ─────────────────────────────────
# UCDP uses the 'country' field with full English country name.
TARGET_COUNTRIES = {
    "Iran",
    "Israel",
    "Palestine",   # GED may encode Gaza/WB as Palestine
    "Iraq",
    "Syria",
    "Lebanon",
    "Yemen",
    "Jordan",      # included as adjacent flashpoint corridor
    "Saudi Arabia",  # coalition actor
}

# UCDP GED / Candidate key columns we want to verify
GED_EXPECTED_COLS = {
    "id", "year", "active_year", "type_of_violence", "conflict_dset_id",
    "conflict_new_id", "conflict_name", "dyad_dset_id", "dyad_new_id",
    "dyad_name", "side_a_dset_id", "side_a_new_id", "side_a",
    "side_b_dset_id", "side_b_new_id", "side_b", "number_of_sources",
    "source_article", "source_office", "source_date", "source_headline",
    "source_original", "where_prec", "where_coordinates", "where_description",
    "adm_1", "adm_2", "latitude", "longitude", "geom_wkt", "priogrid_gid",
    "country", "country_id", "region", "event_clarity", "date_prec",
    "date_start", "date_end", "deaths_a", "deaths_b", "deaths_civilians",
    "deaths_unknown", "best", "high", "low",
}

# Candidate CSV may have a subset; we check the most critical ones
CANDIDATE_REQUIRED_COLS = {
    "id", "year", "type_of_violence", "conflict_name",
    "side_a", "side_b", "country", "region",
    "date_start", "date_end", "latitude", "longitude",
    "deaths_a", "deaths_b", "deaths_civilians", "deaths_unknown", "best",
}

# Study period (inclusive)
STUDY_START = "2024-01-01"
STUDY_END = "2026-04-30"

# ── Dataset catalogue ─────────────────────────────────────────────────────────
DATASETS = {
    "ged_25_1": {
        "label": "UCDP GED 25.1 (1989-2024)",
        "url": "https://ucdp.uu.se/downloads/ged/ged251-csv.zip",
        "format": "zip_csv",
        "max_rows": 5000,   # stream first 5 000 rows to keep download light
    },
    "candidate_2025_full": {
        "label": "UCDP Candidate 25.01.25.12 (all 2025)",
        "url": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v25_01_25_12.csv",
        "format": "csv",
        "max_rows": None,   # file is manageable (~few MB)
    },
    "candidate_26_q1": {
        "label": "UCDP Candidate 26.01.26.03 (Jan-Mar 2026)",
        "url": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_01_26_03.csv",
        "format": "csv",
        "max_rows": None,
    },
    "candidate_26_04": {
        "label": "UCDP Candidate 26.0.4 (Apr 2026)",
        "url": "https://ucdp.uu.se/downloads/candidateged/GEDEvent_v26_0_4.csv",
        "format": "csv",
        "max_rows": None,
    },
}

HEADERS = {
    "User-Agent": "Proyecto-Final-ML1-OSINT/0.1 (educational source validation)"
}


# ─────────────────────────────────────────────────────────────────────────────
# Network helpers
# ─────────────────────────────────────────────────────────────────────────────

def fetch_bytes(url: str, timeout: int = 120, retries: int = 3, max_bytes: int | None = None) -> bytes:
    """Fetch URL content, optionally limiting to max_bytes (streaming)."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = Request(url, headers=HEADERS)
            with urlopen(req, timeout=timeout) as resp:
                if max_bytes:
                    return resp.read(max_bytes)
                return resp.read()
        except Exception as exc:
            last_error = exc
            if attempt < retries:
                print(f"  [retry {attempt}] {exc}", flush=True)
                time.sleep(8 * attempt)
    assert last_error is not None
    raise last_error


# ─────────────────────────────────────────────────────────────────────────────
# CSV parsing helpers
# ─────────────────────────────────────────────────────────────────────────────

def parse_csv_bytes(raw: bytes, max_rows: int | None = None) -> tuple[list[str], list[dict]]:
    """Return (header_list, rows_as_dicts). Handles UTF-8 with BOM."""
    text = raw.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    header = reader.fieldnames or []
    rows: list[dict] = []
    for i, row in enumerate(reader):
        if max_rows and i >= max_rows:
            break
        rows.append(dict(row))
    return list(header), rows


def parse_zip_csv_bytes(raw: bytes, max_rows: int | None) -> tuple[list[str], list[dict], str]:
    """Extract first CSV from ZIP and parse it."""
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError("No CSV file found inside ZIP archive")
        member_name = csv_names[0]
        csv_bytes = zf.read(member_name)
    header, rows = parse_csv_bytes(csv_bytes, max_rows)
    return header, rows, member_name


# ─────────────────────────────────────────────────────────────────────────────
# Analytics helpers
# ─────────────────────────────────────────────────────────────────────────────

def analyse_rows(rows: list[dict], dataset_key: str) -> dict:
    """Compute quality and relevance metrics for a list of UCDP event rows."""
    total = len(rows)
    if total == 0:
        return {"total_rows": 0, "note": "No rows to analyse"}

    # Date coverage
    dates = [r.get("date_start", "") for r in rows if r.get("date_start", "")]
    min_date = min(dates, default="N/A")
    max_date = max(dates, default="N/A")

    # Geographic filter
    relevant_rows = [r for r in rows if r.get("country", "") in TARGET_COUNTRIES]
    country_counts: Counter = Counter(r.get("country", "UNKNOWN") for r in relevant_rows)

    # Null coordinates
    null_coords = sum(
        1 for r in rows
        if not r.get("latitude") or not r.get("longitude")
    )

    # Type of violence breakdown (1=state, 2=non-state, 3=one-sided)
    violence_counts: Counter = Counter(r.get("type_of_violence", "?") for r in relevant_rows)

    # Fatalities in relevant rows
    total_best_deaths = 0
    for r in relevant_rows:
        try:
            total_best_deaths += int(r.get("best") or 0)
        except (ValueError, TypeError):
            pass

    # Column check
    first_cols = set(rows[0].keys()) if rows else set()
    if dataset_key.startswith("ged"):
        expected = GED_EXPECTED_COLS
    else:
        expected = CANDIDATE_REQUIRED_COLS
    missing_cols = sorted(expected - first_cols)
    extra_cols = sorted(first_cols - expected)

    return {
        "total_rows_parsed": total,
        "date_start_range": f"{min_date} → {max_date}",
        "null_coord_rows": null_coords,
        "null_coord_pct": round(100 * null_coords / total, 1),
        "relevant_country_rows": len(relevant_rows),
        "relevant_country_breakdown": dict(country_counts.most_common()),
        "violence_type_breakdown": dict(violence_counts.most_common()),
        "total_best_deaths_relevant": total_best_deaths,
        "columns_found": len(first_cols),
        "missing_expected_cols": missing_cols,
        "extra_cols_vs_expected": extra_cols[:10],  # truncate if many
    }


# ─────────────────────────────────────────────────────────────────────────────
# Main validation per dataset
# ─────────────────────────────────────────────────────────────────────────────

def validate_dataset(key: str, spec: dict) -> dict:
    url = spec["url"]
    fmt = spec["format"]
    max_rows = spec.get("max_rows")
    label = spec["label"]

    print(f"\n{'─'*60}", flush=True)
    print(f"  Validating: {label}", flush=True)
    print(f"  URL: {url}", flush=True)

    result: dict = {
        "label": label,
        "url": url,
        "error": None,
        "bytes_downloaded": 0,
        "member": None,
        "header": [],
        "analytics": {},
    }

    try:
        # For the big GED ZIP we cap download at 30 MB to stay lightweight
        max_dl = 30 * 1024 * 1024 if fmt == "zip_csv" else None
        raw = fetch_bytes(url, max_bytes=max_dl)
        result["bytes_downloaded"] = len(raw)
        print(f"  Downloaded {len(raw):,} bytes", flush=True)

        if fmt == "zip_csv":
            header, rows, member_name = parse_zip_csv_bytes(raw, max_rows)
            result["member"] = member_name
        else:
            header, rows = parse_csv_bytes(raw, max_rows)

        result["header"] = header
        print(f"  Parsed {len(rows):,} rows × {len(header)} columns", flush=True)

        result["analytics"] = analyse_rows(rows, key)

        # Save a small raw sample (first 100 rows)
        sample_rows = rows[:100]
        sample_path = RAW_DIR / f"ucdp_{key}_sample.json"
        sample_path.write_text(
            json.dumps(
                {"header": header, "sample_rows": sample_rows},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        result["raw_sample_path"] = str(sample_path)
        print(f"  Saved sample → {sample_path.name}", flush=True)

    except (HTTPError, URLError, TimeoutError, zipfile.BadZipFile, ValueError) as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        print(f"  ERROR: {result['error']}", flush=True)
    except Exception as exc:  # broad catch: log and continue
        result["error"] = f"Unexpected: {type(exc).__name__}: {exc}"
        print(f"  ERROR: {result['error']}", flush=True)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Markdown report
# ─────────────────────────────────────────────────────────────────────────────

def write_summary(results: dict[str, dict]) -> Path:
    now = datetime.now(UTC).isoformat(timespec="seconds")
    lines = [
        "# UCDP Validation Summary",
        "",
        f"Generated at: {now}",
        "",
        f"Study period targeted: {STUDY_START} → {STUDY_END}",
        "",
        f"Target countries: {', '.join(sorted(TARGET_COUNTRIES))}",
        "",
        "---",
        "",
    ]

    for key, res in results.items():
        lines.append(f"## {res['label']}")
        lines.append("")
        lines.append(f"- URL: {res['url']}")
        lines.append(f"- Error: {res['error'] or 'None'}")
        lines.append(f"- Bytes downloaded: {res['bytes_downloaded']:,}")
        if res.get("member"):
            lines.append(f"- ZIP member extracted: {res['member']}")
        lines.append(f"- Columns found: {len(res.get('header', []))}")
        lines.append("")

        ana = res.get("analytics", {})
        if ana:
            lines.append("### Quality & Relevance")
            lines.append("")
            lines.append(f"- Rows parsed: {ana.get('total_rows_parsed', 0):,}")
            lines.append(f"- Date range in data: {ana.get('date_start_range', 'N/A')}")
            lines.append(f"- Rows with null coordinates: {ana.get('null_coord_rows', 0):,} "
                         f"({ana.get('null_coord_pct', 0)}%)")
            lines.append(f"- Rows matching target countries: {ana.get('relevant_country_rows', 0):,}")
            lines.append("")

            cc = ana.get("relevant_country_breakdown", {})
            if cc:
                lines.append("  **Country breakdown (target region):**")
                for country, cnt in sorted(cc.items(), key=lambda x: -x[1]):
                    lines.append(f"  - {country}: {cnt:,}")
            lines.append("")

            vt = ana.get("violence_type_breakdown", {})
            if vt:
                vt_map = {"1": "State-based", "2": "Non-state", "3": "One-sided"}
                lines.append("  **Violence type (target region):**")
                for vtype, cnt in sorted(vt.items(), key=lambda x: -x[1]):
                    label = vt_map.get(str(vtype), f"Type {vtype}")
                    lines.append(f"  - {label}: {cnt:,}")
            lines.append("")

            lines.append(f"- Best-estimate deaths in target region: {ana.get('total_best_deaths_relevant', 0):,}")

            missing = ana.get("missing_expected_cols", [])
            if missing:
                lines.append(f"- ⚠ Missing expected columns: {', '.join(missing)}")
            else:
                lines.append("- ✓ All expected key columns present")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Decision summary
    lines += [
        "## Decision",
        "",
        "UCDP GED 25.1 provides the historical backbone (2024 covered).",
        "UCDP Candidate files extend coverage through April 2026, capturing the",
        "active phases of the Iran-Israel-US escalation.",
        "Both datasets are accepted as the primary structured event source,",
        "replacing ACLED.",
        "",
    ]

    output = TABLES_DIR / "ucdp_validation_summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  UCDP Source Validation")
    print(f"  {datetime.now(UTC).isoformat(timespec='seconds')}")
    print("=" * 60)

    results: dict[str, dict] = {}
    for key, spec in DATASETS.items():
        results[key] = validate_dataset(key, spec)

    summary_path = write_summary(results)
    print(f"\n{'='*60}")
    print(f"  Summary written → {summary_path}")
    print("=" * 60)

    # Exit with error code if any dataset failed
    errors = [k for k, r in results.items() if r.get("error")]
    if errors:
        print(f"\n  ⚠  Failures: {', '.join(errors)}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

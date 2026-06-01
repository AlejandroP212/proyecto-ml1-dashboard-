"""Validate small GDELT samples for Phase 2.

This script is intentionally small and conservative. It fetches a limited DOC API
sample and tiny GDELT 2.0 raw files for one timestamp, then writes a plain-text
summary that can be reviewed before building full ingestion pipelines.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
TABLES_DIR = ROOT / "reports" / "tables"

DOC_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_V2_BASE_URL = "http://data.gdeltproject.org/gdeltv2"

REGION_COUNTRY_CODES = {
    "IR": "Iran",
    "IS": "Israel",
    "WE": "West Bank",
    "GZ": "Gaza Strip",
    "IZ": "Iraq",
    "SY": "Syria",
    "LE": "Lebanon",
    "YM": "Yemen",
}

EVENT_COLUMNS = [
    "GLOBALEVENTID",
    "SQLDATE",
    "MonthYear",
    "Year",
    "FractionDate",
    "Actor1Code",
    "Actor1Name",
    "Actor1CountryCode",
    "Actor1KnownGroupCode",
    "Actor1EthnicCode",
    "Actor1Religion1Code",
    "Actor1Religion2Code",
    "Actor1Type1Code",
    "Actor1Type2Code",
    "Actor1Type3Code",
    "Actor2Code",
    "Actor2Name",
    "Actor2CountryCode",
    "Actor2KnownGroupCode",
    "Actor2EthnicCode",
    "Actor2Religion1Code",
    "Actor2Religion2Code",
    "Actor2Type1Code",
    "Actor2Type2Code",
    "Actor2Type3Code",
    "IsRootEvent",
    "EventCode",
    "EventBaseCode",
    "EventRootCode",
    "QuadClass",
    "GoldsteinScale",
    "NumMentions",
    "NumSources",
    "NumArticles",
    "AvgTone",
    "Actor1Geo_Type",
    "Actor1Geo_FullName",
    "Actor1Geo_CountryCode",
    "Actor1Geo_ADM1Code",
    "Actor1Geo_ADM2Code",
    "Actor1Geo_Lat",
    "Actor1Geo_Long",
    "Actor1Geo_FeatureID",
    "Actor2Geo_Type",
    "Actor2Geo_FullName",
    "Actor2Geo_CountryCode",
    "Actor2Geo_ADM1Code",
    "Actor2Geo_ADM2Code",
    "Actor2Geo_Lat",
    "Actor2Geo_Long",
    "Actor2Geo_FeatureID",
    "ActionGeo_Type",
    "ActionGeo_FullName",
    "ActionGeo_CountryCode",
    "ActionGeo_ADM1Code",
    "ActionGeo_ADM2Code",
    "ActionGeo_Lat",
    "ActionGeo_Long",
    "ActionGeo_FeatureID",
    "DATEADDED",
    "SOURCEURL",
]

MENTION_COLUMNS = [
    "GLOBALEVENTID",
    "EventTimeDate",
    "MentionTimeDate",
    "MentionType",
    "MentionSourceName",
    "MentionIdentifier",
    "SentenceID",
    "Actor1CharOffset",
    "Actor2CharOffset",
    "ActionCharOffset",
    "InRawText",
    "Confidence",
    "MentionDocLen",
    "MentionDocTone",
    "MentionDocTranslationInfo",
    "Extras",
]

GKG_COLUMNS = [
    "GKGRECORDID",
    "DATE",
    "SourceCollectionIdentifier",
    "SourceCommonName",
    "DocumentIdentifier",
    "Counts",
    "V2Counts",
    "Themes",
    "V2Themes",
    "Locations",
    "V2Locations",
    "Persons",
    "V2Persons",
    "Organizations",
    "V2Organizations",
    "V2Tone",
    "Dates",
    "GCAM",
    "SharingImage",
    "RelatedImages",
    "SocialImageEmbeds",
    "SocialVideoEmbeds",
    "Quotations",
    "AllNames",
    "Amounts",
    "TranslationInfo",
    "Extras",
]


def fetch_bytes(url: str, timeout: int = 30, retries: int = 3) -> bytes:
    headers = {
        "User-Agent": "Proyecto-Final-ML1-OSINT/0.1 (educational source validation)"
    }
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            request = Request(url, headers=headers)
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except Exception as exc:  # Keep this broad: network validation must report failures.
            last_error = exc
            if attempt < retries:
                time.sleep(5 * attempt)
    assert last_error is not None
    raise last_error


def fetch_doc_sample() -> dict:
    params = {
        "query": "(Iran OR Israel)",
        "mode": "artlist",
        "format": "json",
        "maxrecords": 10,
        "startdatetime": "20260508000000",
        "enddatetime": "20260508235959",
    }
    url = f"{DOC_API_URL}?{urlencode(params)}"
    output = RAW_DIR / "gdelt_doc_2026-05-08_sample.json"
    try:
        payload = fetch_bytes(url)
        data = json.loads(payload.decode("utf-8"))
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"url": url, "output": output, "data": data, "error": None}
    except (HTTPError, URLError, TimeoutError) as exc:
        data = {"articles": [], "error": f"{type(exc).__name__}: {exc}"}
        output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"url": url, "output": output, "data": data, "error": data["error"]}


def read_zipped_tsv(
    url: str,
    columns: list[str],
    max_rows: int | None = None,
    keep_rows: bool = False,
) -> dict:
    payload = fetch_bytes(url)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = archive.namelist()
        if not names:
            raise ValueError(f"ZIP file has no members: {url}")
        with archive.open(names[0]) as handle:
            text = io.TextIOWrapper(handle, encoding="utf-8", errors="replace")
            reader = csv.reader(text, delimiter="\t")
            rows = []
            for index, row in enumerate(reader):
                if max_rows is not None and index >= max_rows:
                    break
                rows.append(row)
    result = {
        "url": url,
        "zip_bytes": len(payload),
        "member": names[0],
        "rows_read": len(rows),
        "expected_columns": len(columns),
        "observed_columns_first_row": len(rows[0]) if rows else 0,
        "sample": [dict(zip(columns, row)) for row in rows[:5]],
    }
    if keep_rows:
        result["_rows"] = [dict(zip(columns, row)) for row in rows]
    return result


def summarize_relevant_event_rows(rows: list[dict[str, str]]) -> dict:
    relevant = []
    for row in rows:
        codes = {
            row.get("Actor1CountryCode", ""),
            row.get("Actor2CountryCode", ""),
            row.get("ActionGeo_CountryCode", ""),
        }
        matched = sorted(code for code in codes if code in REGION_COUNTRY_CODES)
        if matched:
            relevant.append(
                {
                    "GLOBALEVENTID": row.get("GLOBALEVENTID", ""),
                    "SQLDATE": row.get("SQLDATE", ""),
                    "Actor1Name": row.get("Actor1Name", ""),
                    "Actor1CountryCode": row.get("Actor1CountryCode", ""),
                    "Actor2Name": row.get("Actor2Name", ""),
                    "Actor2CountryCode": row.get("Actor2CountryCode", ""),
                    "EventCode": row.get("EventCode", ""),
                    "EventRootCode": row.get("EventRootCode", ""),
                    "GoldsteinScale": row.get("GoldsteinScale", ""),
                    "AvgTone": row.get("AvgTone", ""),
                    "ActionGeo_FullName": row.get("ActionGeo_FullName", ""),
                    "ActionGeo_CountryCode": row.get("ActionGeo_CountryCode", ""),
                    "matched_region_codes": ",".join(matched),
                    "SOURCEURL": row.get("SOURCEURL", ""),
                }
            )
    counts: dict[str, int] = {}
    for row in relevant:
        for code in row["matched_region_codes"].split(","):
            counts[code] = counts.get(code, 0) + 1
    return {
        "relevant_rows": relevant[:20],
        "relevant_count": len(relevant),
        "relevant_country_counts": counts,
    }


def validate_raw_files() -> dict:
    timestamp = "20260508000000"
    specs = {
        "events": (f"{GDELT_V2_BASE_URL}/{timestamp}.export.CSV.zip", EVENT_COLUMNS),
        "mentions": (f"{GDELT_V2_BASE_URL}/{timestamp}.mentions.CSV.zip", MENTION_COLUMNS),
        "gkg": (f"{GDELT_V2_BASE_URL}/{timestamp}.gkg.csv.zip", GKG_COLUMNS),
    }
    results = {}
    for name, (url, columns) in specs.items():
        results[name] = read_zipped_tsv(url, columns, keep_rows=(name == "events"))
        if name == "events":
            event_rows = results[name].pop("_rows")
            results[name]["relevance"] = summarize_relevant_event_rows(event_rows)
        output = RAW_DIR / f"gdelt_{name}_{timestamp}_sample.json"
        output.write_text(
            json.dumps(results[name], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return results


def summarize(doc_result: dict, raw_results: dict) -> Path:
    articles = doc_result["data"].get("articles", [])
    languages = sorted({article.get("language", "") for article in articles if article.get("language")})
    countries = sorted(
        {article.get("sourcecountry", "") for article in articles if article.get("sourcecountry")}
    )
    domains = sorted({article.get("domain", "") for article in articles if article.get("domain")})

    lines = [
        "# GDELT validation summary",
        "",
        f"Generated at: {datetime.now(UTC).isoformat(timespec='seconds')}",
        "",
        "## DOC API sample",
        "",
        f"- Query URL: {doc_result['url']}",
        f"- Error: {doc_result['error'] or 'None'}",
        f"- Articles returned: {len(articles)}",
        f"- Languages: {', '.join(languages) if languages else 'N/A'}",
        f"- Source countries: {', '.join(countries) if countries else 'N/A'}",
        f"- Domains observed: {', '.join(domains[:15]) if domains else 'N/A'}",
        f"- Raw output: {doc_result['output']}",
        "",
        "## Raw GDELT 2.0 files",
        "",
    ]

    for name, result in raw_results.items():
        lines.extend(
            [
                f"### {name}",
                "",
                f"- URL: {result['url']}",
                f"- ZIP bytes: {result['zip_bytes']}",
                f"- ZIP member: {result['member']}",
                f"- Rows read: {result['rows_read']}",
                f"- Expected columns: {result['expected_columns']}",
                f"- Observed columns in first row: {result['observed_columns_first_row']}",
                "",
            ]
        )
        if name == "events":
            relevance = result.get("relevance", {})
            country_counts = relevance.get("relevant_country_counts", {})
            counts_text = ", ".join(
                f"{code}={count}" for code, count in sorted(country_counts.items())
            )
            lines.extend(
                [
                    "- Region-code hits in this 15-minute event file: "
                    f"{relevance.get('relevant_count', 0)}",
                    f"- Region-code breakdown: {counts_text or 'N/A'}",
                    "",
                ]
            )

    output = TABLES_DIR / "gdelt_validation_summary.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    doc_result = fetch_doc_sample()
    raw_results = validate_raw_files()
    summary = summarize(doc_result, raw_results)
    print(f"Wrote validation summary: {summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

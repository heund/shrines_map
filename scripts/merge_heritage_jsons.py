import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PRIMARY_PATH = PROJECT_ROOT / "heritage" / "jeju_heritage_sites.json"
SECONDARY_PATH = PROJECT_ROOT / "heritage" / "jeju_historic_locations.json"
OUTPUT_PATH = PROJECT_ROOT / "heritage" / "combined_heritage_sites.json"

OUTPUT_FIELDS = [
    "ccmaName",
    "gcodeName",
    "name",
    "description",
    "image",
    "latitude",
    "longitude",
]


def normalize_name(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u3131-\u318E\uAC00-\uD7A3]+", "", value or "").lower()


def normalize_primary_row(row: dict) -> dict:
    return {
        "ccmaName": row.get("ccmaName"),
        "gcodeName": row.get("gcodeName"),
        "name": row.get("name"),
        "description": row.get("description"),
        "image": row.get("image"),
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
    }


def normalize_secondary_row(row: dict) -> dict:
    return {
        "ccmaName": None,
        "gcodeName": None,
        "name": row.get("name"),
        "description": None,
        "image": None,
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
    }


def main() -> int:
    if not PRIMARY_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {PRIMARY_PATH}")
    if not SECONDARY_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {SECONDARY_PATH}")

    primary_rows = json.loads(PRIMARY_PATH.read_text(encoding="utf-8"))
    secondary_rows = json.loads(SECONDARY_PATH.read_text(encoding="utf-8"))

    combined_rows = []
    seen_names = set()
    seen_exact_coords = set()

    for row in primary_rows:
        normalized = normalize_primary_row(row)
        combined_rows.append(normalized)
        if normalized["name"]:
            seen_names.add(normalize_name(normalized["name"]))
        if normalized["latitude"] and normalized["longitude"]:
            seen_exact_coords.add((normalized["latitude"], normalized["longitude"]))

    for row in secondary_rows:
        normalized = normalize_secondary_row(row)
        normalized_name = normalize_name(normalized["name"] or "")
        exact_coords = (normalized["latitude"], normalized["longitude"])
        if normalized_name and normalized_name in seen_names:
            continue
        if normalized["latitude"] and normalized["longitude"] and exact_coords in seen_exact_coords:
            continue
        combined_rows.append(normalized)
        if normalized_name:
            seen_names.add(normalized_name)
        if normalized["latitude"] and normalized["longitude"]:
            seen_exact_coords.add(exact_coords)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as outfile:
        json.dump(combined_rows, outfile, ensure_ascii=False, indent=2)

    print(f"Primary rows: {len(primary_rows)}")
    print(f"Secondary rows: {len(secondary_rows)}")
    print(f"Combined rows: {len(combined_rows)}")
    print(f"Wrote JSON: {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

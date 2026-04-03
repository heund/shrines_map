import csv
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "shrine" / "standardized_shrines_korean.csv"
OUTPUT_PATH = PROJECT_ROOT / "shrine" / "final_shrines.json"

FIELDS = [
    "latitude",
    "longitude",
    "ownership_standardized",
    "validated_address_ko",
    "shrine_name",
]


def from_csv_value(value: str):
    if value == "NULL":
        return None
    return value


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    output_rows = []
    for row in rows:
        output_rows.append(
            {
                "latitude": from_csv_value(row.get("latitude", "NULL")),
                "longitude": from_csv_value(row.get("longitude", "NULL")),
                "ownership_standardized": from_csv_value(row.get("ownership_standardized", "NULL")),
                "validated_address_ko": from_csv_value(row.get("validated_address_ko", "NULL")),
                "shrine_name": from_csv_value(row.get("shrine_name", "NULL")),
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as outfile:
        json.dump(output_rows, outfile, ensure_ascii=False, indent=2)

    print(f"Processed {len(output_rows)} rows.")
    print(f"Wrote JSON: {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

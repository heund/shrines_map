import csv
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "shrine" / "standardized_shrines_korean_withID.csv"
SOURCE_PATH = PROJECT_ROOT / "shrine" / "shrines.csv"
OUTPUT_PATH = PROJECT_ROOT / "shrine" / "final_shrines.json"


def from_csv_value(value: str):
    if value == "NULL":
        return None
    return value


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {SOURCE_PATH}")

    with SOURCE_PATH.open("r", encoding="utf-8-sig", newline="") as infile:
        source_rows = list(csv.DictReader(infile))

    source_status_by_id = {
        (row.get("No.") or "").strip(): row.get("상태", "")
        for row in source_rows
        if (row.get("No.") or "").strip()
    }

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    output_rows = []
    for row in rows:
        shrine_id = from_csv_value(row.get("ID", "NULL"))
        shrine_id_key = str(shrine_id) if shrine_id is not None else ""
        output_rows.append(
            {
                "ID": shrine_id,
                "status": from_csv_value(row.get("status", "NULL")),
                "상태": from_csv_value(source_status_by_id.get(shrine_id_key, "NULL")),
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

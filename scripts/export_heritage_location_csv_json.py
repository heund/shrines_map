import csv
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = next((PROJECT_ROOT / "heritage").glob("*위치정보_cleaned.csv"))
OUTPUT_PATH = PROJECT_ROOT / "heritage" / "jeju_historic_locations.json"


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
                "latitude": row.get("위도", "").strip() or None,
                "longitude": row.get("경도", "").strip() or None,
                "name": row.get("장소명", "").strip() or None,
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

import csv
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = PROJECT_ROOT / "shrine" / "shrines.csv"
TARGET_PATH = PROJECT_ROOT / "shrine" / "standardized_shrines_korean_withID.csv"
FALLBACK_OUTPUT_PATH = PROJECT_ROOT / "shrine" / "standardized_shrines_korean_withID_with_status.csv"

SOURCE_ID_FIELD = "No."
SOURCE_STATUS_FIELD = "상태"
TARGET_ID_FIELD = "ID"
TARGET_OWNERSHIP_RAW_FIELD = "ownership_raw"


def main() -> int:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {SOURCE_PATH}")
    if not TARGET_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {TARGET_PATH}")

    with SOURCE_PATH.open("r", encoding="utf-8-sig", newline="") as infile:
        source_rows = list(csv.DictReader(infile))

    source_status_by_id = {}
    for row in source_rows:
        source_id = (row.get(SOURCE_ID_FIELD) or "").strip()
        if not source_id:
            continue
        source_status_by_id[source_id] = row.get(SOURCE_STATUS_FIELD, "")

    with TARGET_PATH.open("r", encoding="utf-8-sig", newline="") as infile:
        target_rows = list(csv.DictReader(infile))

    if not target_rows:
        raise ValueError("Target CSV is empty.")

    output_fieldnames = list(target_rows[0].keys())
    if SOURCE_STATUS_FIELD not in output_fieldnames:
        insert_at = output_fieldnames.index(TARGET_OWNERSHIP_RAW_FIELD) + 1
        output_fieldnames.insert(insert_at, SOURCE_STATUS_FIELD)

    output_rows = []
    for row in target_rows:
        target_id = (row.get(TARGET_ID_FIELD) or "").strip()
        if not target_id:
            raise ValueError("Encountered target row without ID.")
        if target_id not in source_status_by_id:
            raise ValueError(f"No matching source row found for ID {target_id}.")

        output_row = {}
        for fieldname in output_fieldnames:
            if fieldname == SOURCE_STATUS_FIELD:
                output_row[fieldname] = source_status_by_id[target_id]
            else:
                output_row[fieldname] = row.get(fieldname, "")
        output_rows.append(output_row)

    output_path = TARGET_PATH
    try:
        with output_path.open("w", encoding="utf-8-sig", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)
    except PermissionError:
        output_path = FALLBACK_OUTPUT_PATH
        with output_path.open("w", encoding="utf-8-sig", newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
            writer.writeheader()
            writer.writerows(output_rows)

    print(f"Processed {len(output_rows)} rows.")
    print(f"Updated CSV: {output_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

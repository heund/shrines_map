import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "documentation" / "venue_location.md"
OUTPUT_PATH = PROJECT_ROOT / "venue" / "venues.json"

LINE_PATTERN = re.compile(r"^(?P<name>.+?)\s+(?P<latitude>-?\d+\.\d+),\s*(?P<longitude>-?\d+\.\d+)\s*$")


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    lines = INPUT_PATH.read_text(encoding="utf-8").splitlines()
    output_rows = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("http"):
            continue
        match = LINE_PATTERN.match(stripped)
        if not match:
            continue
        output_rows.append(
            {
                "latitude": match.group("latitude"),
                "longitude": match.group("longitude"),
                "name": match.group("name"),
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as outfile:
        json.dump(output_rows, outfile, ensure_ascii=False, indent=2)

    print(f"Processed {len(output_rows)} venues.")
    print(f"Wrote JSON: {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

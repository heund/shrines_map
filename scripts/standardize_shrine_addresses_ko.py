import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "shrine" / "cleaned_shrines.csv"
OUTPUT_PATH = PROJECT_ROOT / "shrine" / "standardized_shrines_korean.csv"
ENV_PATH = PROJECT_ROOT / ".env"

KAKAO_COORD2ADDRESS_API_URL = "https://dapi.kakao.com/v2/local/geo/coord2address.json"
KAKAO_REST_API_KEY_ENV = "KAKAO_REST_API_KEY"

OUTPUT_FIELDS = [
    "region",
    "shrine_name",
    "raw_address",
    "combined_address",
    "resolved_address",
    "latitude",
    "longitude",
    "status",
    "ownership_raw",
    "ownership_standardized",
    "validated_address_ko",
    "validated_road_address_ko",
    "validated_jibun_address_ko",
    "address_validation_status",
    "address_validation_source",
]


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def request_json(url: str, headers: Dict[str, str]) -> Dict:
    request = Request(url, headers=headers)
    attempts = 3
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError):
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))
    return {}


def to_csv_value(value: Optional[str]) -> str:
    if value is None or value == "":
        return "NULL"
    return value


def reverse_geocode_kakao(
    longitude: str,
    latitude: str,
    rest_api_key: str,
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    params = urlencode(
        {
            "x": longitude,
            "y": latitude,
            "input_coord": "WGS84",
        }
    )
    payload = request_json(
        f"{KAKAO_COORD2ADDRESS_API_URL}?{params}",
        {
            "Authorization": f"KakaoAK {rest_api_key}",
            "User-Agent": "Codex Shrine Address Standardizer/1.0",
        },
    )
    documents = payload.get("documents", []) if isinstance(payload, dict) else []
    if len(documents) != 1:
        return None, None, None

    document = documents[0]
    road_address = document.get("road_address") or {}
    jibun_address = document.get("address") or {}

    road_address_ko = (road_address.get("address_name") or "").strip() or None
    jibun_address_ko = (jibun_address.get("address_name") or "").strip() or None
    validated_address_ko = road_address_ko or jibun_address_ko
    if not validated_address_ko:
        return None, None, None
    return validated_address_ko, road_address_ko, jibun_address_ko


def main() -> int:
    load_env_file(ENV_PATH)
    kakao_rest_api_key = os.environ.get(KAKAO_REST_API_KEY_ENV, "").strip()

    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")
    if not kakao_rest_api_key:
        raise RuntimeError(
            f"Missing required environment variable: {KAKAO_REST_API_KEY_ENV}"
        )

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as infile:
        input_rows = list(csv.DictReader(infile))

    output_rows = []
    reverse_geocode_cache: Dict[Tuple[str, str], Tuple[Optional[str], Optional[str], Optional[str]]] = {}

    for row in input_rows:
        latitude = row.get("latitude", "")
        longitude = row.get("longitude", "")
        status = row.get("status", "")

        validated_address_ko = None
        validated_road_address_ko = None
        validated_jibun_address_ko = None
        address_validation_status = "unresolved"
        address_validation_source = "kakao_coord2address"

        if status == "resolved" and latitude != "NULL" and longitude != "NULL":
            cache_key = (longitude, latitude)
            if cache_key not in reverse_geocode_cache:
                reverse_geocode_cache[cache_key] = reverse_geocode_kakao(
                    longitude=longitude,
                    latitude=latitude,
                    rest_api_key=kakao_rest_api_key,
                )
                time.sleep(0.3)
            (
                validated_address_ko,
                validated_road_address_ko,
                validated_jibun_address_ko,
            ) = reverse_geocode_cache[cache_key]
            if validated_address_ko:
                address_validation_status = "validated"

        output_rows.append(
            {
                "region": row.get("region", ""),
                "shrine_name": row.get("shrine_name", ""),
                "raw_address": row.get("raw_address", ""),
                "combined_address": row.get("combined_address", ""),
                "resolved_address": row.get("resolved_address", ""),
                "latitude": latitude,
                "longitude": longitude,
                "status": status,
                "ownership_raw": row.get("ownership_raw", ""),
                "ownership_standardized": row.get("ownership_standardized", ""),
                "validated_address_ko": to_csv_value(validated_address_ko),
                "validated_road_address_ko": to_csv_value(validated_road_address_ko),
                "validated_jibun_address_ko": to_csv_value(validated_jibun_address_ko),
                "address_validation_status": address_validation_status,
                "address_validation_source": address_validation_source,
            }
        )

    if len(output_rows) != len(input_rows):
        raise ValueError("Output row count does not match input row count.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Processed {len(output_rows)} rows.")
    print(f"Wrote CSV: {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

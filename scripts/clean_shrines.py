import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = PROJECT_ROOT / "shrine" / "shrines.csv"
OUTPUT_CSV_PATH = PROJECT_ROOT / "shrine" / "cleaned_shrines.csv"
OUTPUT_JSON_PATH = PROJECT_ROOT / "shrine" / "cleaned_shrines.json"
ENV_PATH = PROJECT_ROOT / ".env"

COL_REGION = "\uC9C0\uC5ED"
COL_SHRINE_NAME = "\uC2E0\uB2F9\uBA85"
COL_ADDRESS = "\uC8FC\uC18C"
COL_OWNERSHIP = "\uC18C\uC720\uAD8C"

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
]

VALID_STATUSES = {"resolved", "partial", "unresolved"}
VAGUE_TERMS = {
    "\uD574\uBCC0",
    "beach",
    "near coast",
}
ADMIN_KEYWORDS = {
    "\uAD6D\uAC00",
    "\uC81C\uC8FC\uB3C4",
    "\uC81C\uC8FC\uC2DC",
    "\uD589\uC815",
    "\uB3C4\uCCAD",
    "\uC2DC\uCCAD",
    "\uAD70\uCCAD",
    "\uAD6C\uCCAD",
}
CORPORATE_KEYWORDS = {
    "\uBC95\uC778",
    "\uC7AC\uB2E8",
    "\uD68C\uC0AC",
    "\uAE30\uC5C5",
    "corporation",
    "foundation",
    "company",
}
KAKAO_API_URL = "https://dapi.kakao.com/v2/local/search/address.json"
GOOGLE_GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"
KAKAO_REST_API_KEY_ENV = "KAKAO_REST_API_KEY"
GOOGLE_MAPS_API_KEY_ENV = "GOOGLE_MAPS_API_KEY"


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


load_env_file(ENV_PATH)
KAKAO_REST_API_KEY = os.environ.get(KAKAO_REST_API_KEY_ENV, "").strip()
GOOGLE_MAPS_API_KEY = os.environ.get(GOOGLE_MAPS_API_KEY_ENV, "").strip()


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def is_invalid_address(raw_address: str) -> bool:
    normalized = normalize_space(raw_address)
    lowered = normalized.casefold()
    if not normalized:
        return True
    if lowered == "null":
        return True
    if lowered == "gps error":
        return True
    if "gps" in lowered and ("\uC624\uB958" in normalized or "error" in lowered):
        return True
    return False


def is_vague_address(raw_address: str) -> bool:
    normalized = normalize_space(raw_address)
    lowered = normalized.casefold()
    if lowered in VAGUE_TERMS:
        return True
    if not any(char.isdigit() for char in normalized):
        return True
    return False


def classify_address(raw_address: str) -> str:
    if is_invalid_address(raw_address):
        return "invalid"
    if is_vague_address(raw_address):
        return "vague"
    return "valid"


def combine_address(region: str, raw_address: str, classification: str) -> Optional[str]:
    if classification == "invalid":
        return None
    return normalize_space(f"{region} {raw_address}")


def standardize_ownership(raw_value: str) -> str:
    normalized = normalize_space(raw_value)
    lowered = normalized.casefold()
    if not normalized or lowered == "null" or normalized == "-":
        return "\uBBF8\uC0C1"
    if "\uACF5\uB3D9" in normalized or ("\uAC1C\uC778" in normalized and "\uACF5\uB3D9" in normalized):
        return "\uACF5\uB3D9"
    if any(keyword in normalized for keyword in ADMIN_KEYWORDS):
        return "\uAD6D\uAC00"
    if any(keyword in lowered for keyword in {item.casefold() for item in CORPORATE_KEYWORDS}):
        return "\uBC95\uC778"
    if "\uAC1C\uC778" in normalized:
        return "\uAC1C\uC778"
    return "\uBBF8\uC0C1"


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


def geocode_with_kakao(combined_address: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    rest_api_key = KAKAO_REST_API_KEY
    if not rest_api_key:
        return None, None, None

    params = urlencode(
        {
            "query": combined_address,
            "analyze_type": "similar",
            "page": 1,
            "size": 2,
        }
    )
    payload = request_json(
        f"{KAKAO_API_URL}?{params}",
        {
            "Authorization": f"KakaoAK {rest_api_key}",
            "User-Agent": "Codex Shrine Cleaner/1.0",
        },
    )
    documents = payload.get("documents", []) if isinstance(payload, dict) else []
    if len(documents) != 1:
        return None, None, None
    document = documents[0]
    road_address = document.get("road_address") or {}
    address = document.get("address") or {}
    resolved_address = (road_address.get("address_name") or address.get("address_name") or "").strip()
    latitude = (document.get("y") or "").strip()
    longitude = (document.get("x") or "").strip()
    if not resolved_address or not latitude or not longitude:
        return None, None, None
    return resolved_address, latitude, longitude


def geocode_with_google(combined_address: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    api_key = GOOGLE_MAPS_API_KEY
    if not api_key:
        return None, None, None

    params = urlencode(
        {
            "address": combined_address,
            "region": "kr",
            "key": api_key,
        }
    )
    payload = request_json(
        f"{GOOGLE_GEOCODING_API_URL}?{params}",
        {
            "User-Agent": "Codex Shrine Cleaner/1.0",
        },
    )
    if not isinstance(payload, dict):
        return None, None, None

    status = (payload.get("status") or "").strip()
    results = payload.get("results", [])
    if status != "OK" or len(results) != 1:
        return None, None, None

    result = results[0]
    formatted_address = (result.get("formatted_address") or "").strip()
    location = ((result.get("geometry") or {}).get("location") or {})
    latitude = location.get("lat")
    longitude = location.get("lng")
    if not formatted_address or latitude is None or longitude is None:
        return None, None, None
    return formatted_address, str(latitude), str(longitude)


def geocode_address(combined_address: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    kakao_result = geocode_with_kakao(combined_address)
    if kakao_result != (None, None, None):
        return kakao_result
    return geocode_with_google(combined_address)


def to_csv_value(value: Optional[str]) -> str:
    if value is None:
        return "NULL"
    return value


def main() -> int:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")
    if not KAKAO_REST_API_KEY:
        raise RuntimeError(
            f"Missing required environment variable: {KAKAO_REST_API_KEY_ENV}"
        )

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        input_rows = list(reader)

    output_rows = []
    json_rows = []
    geocode_cache: Dict[str, Tuple[Optional[str], Optional[str], Optional[str]]] = {}

    for row in input_rows:
        region = normalize_space(row.get(COL_REGION, "") or "")
        shrine_name = normalize_space(row.get(COL_SHRINE_NAME, "") or "")
        raw_address = normalize_space(row.get(COL_ADDRESS, "") or "")
        ownership_raw = normalize_space(row.get(COL_OWNERSHIP, "") or "")

        classification = classify_address(raw_address)
        combined_address = combine_address(region, raw_address, classification)
        resolved_address = None
        latitude = None
        longitude = None

        if classification == "valid" and combined_address is not None:
            if combined_address not in geocode_cache:
                geocode_cache[combined_address] = geocode_address(combined_address)
                time.sleep(0.5)
            resolved_address, latitude, longitude = geocode_cache[combined_address]

        if classification == "vague":
            status = "partial"
        elif resolved_address is not None and latitude is not None and longitude is not None:
            status = "resolved"
        else:
            status = "unresolved"

        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status generated: {status}")

        ownership_standardized = standardize_ownership(ownership_raw)

        csv_row = {
            "region": region,
            "shrine_name": shrine_name,
            "raw_address": to_csv_value(raw_address or None),
            "combined_address": to_csv_value(combined_address),
            "resolved_address": to_csv_value(resolved_address),
            "latitude": to_csv_value(latitude),
            "longitude": to_csv_value(longitude),
            "status": status,
            "ownership_raw": to_csv_value(ownership_raw or None),
            "ownership_standardized": ownership_standardized,
        }
        json_row = {
            "region": region,
            "shrine_name": shrine_name,
            "raw_address": raw_address or None,
            "combined_address": combined_address,
            "resolved_address": resolved_address,
            "latitude": latitude,
            "longitude": longitude,
            "status": status,
            "ownership_raw": ownership_raw or None,
            "ownership_standardized": ownership_standardized,
        }

        output_rows.append(csv_row)
        json_rows.append(json_row)

    if len(output_rows) != len(input_rows):
        raise ValueError("Output row count does not match input row count.")

    for row in output_rows:
        for field in OUTPUT_FIELDS:
            if field not in row:
                raise ValueError(f"Missing required output field: {field}")

    OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV_PATH.open("w", encoding="utf-8-sig", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)

    with OUTPUT_JSON_PATH.open("w", encoding="utf-8", newline="") as outfile:
        json.dump(json_rows, outfile, ensure_ascii=False, indent=2)

    print(f"Processed {len(output_rows)} rows.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

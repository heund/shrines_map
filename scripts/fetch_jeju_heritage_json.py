import json
import math
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "heritage" / "jeju_heritage_sites.json"

LIST_API_URL = "https://www.khs.go.kr/cha/SearchKindOpenapiList.do"
DETAIL_API_URL = "https://www.khs.go.kr/cha/SearchKindOpenapiDt.do"
JEJU_CTCD = "50"
PAGE_UNIT = 100


def request_text(url: str) -> str:
    request = Request(url, headers={"User-Agent": "Codex Heritage Fetcher/1.0"})
    attempts = 3
    for attempt in range(attempts):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except (HTTPError, URLError):
            if attempt == attempts - 1:
                raise
            time.sleep(2 * (attempt + 1))
    return ""


def get_text(element: Optional[ET.Element], tag_name: str) -> str:
    if element is None:
        return ""
    child = element.find(tag_name)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


def normalize_description(text: str) -> str:
    return " ".join(text.split())


def parse_list_page(page_index: int) -> Dict:
    params = urlencode(
        {
            "pageUnit": PAGE_UNIT,
            "pageIndex": page_index,
            "ccbaCtcd": JEJU_CTCD,
        }
    )
    xml_text = request_text(f"{LIST_API_URL}?{params}")
    root = ET.fromstring(xml_text)
    total_count = int(get_text(root, "totalCnt") or "0")
    items = []
    for item in root.findall("item"):
        items.append(
            {
                "ccbaKdcd": get_text(item, "ccbaKdcd"),
                "ccbaAsno": get_text(item, "ccbaAsno"),
                "ccbaCtcd": get_text(item, "ccbaCtcd"),
            }
        )
    return {
        "total_count": total_count,
        "items": items,
    }


def parse_detail_item(ccba_kdcd: str, ccba_asno: str, ccba_ctcd: str) -> Dict:
    params = urlencode(
        {
            "ccbaKdcd": ccba_kdcd,
            "ccbaAsno": ccba_asno,
            "ccbaCtcd": ccba_ctcd,
        }
    )
    xml_text = request_text(f"{DETAIL_API_URL}?{params}")
    root = ET.fromstring(xml_text)
    item = root.find("item")

    name = get_text(item, "ccbaMnm1")
    ccma_name = get_text(item, "ccmaName")
    gcode_name = get_text(item, "gcodeName")
    description = normalize_description(get_text(item, "content"))
    image = get_text(item, "imageUrl")
    latitude = get_text(root, "latitude")
    longitude = get_text(root, "longitude")

    if latitude == "0":
        latitude = ""
    if longitude == "0":
        longitude = ""

    return {
        "ccmaName": ccma_name or None,
        "gcodeName": gcode_name or None,
        "name": name or None,
        "description": description or None,
        "image": image or None,
        "latitude": latitude or None,
        "longitude": longitude or None,
    }


def main() -> int:
    first_page = parse_list_page(page_index=1)
    total_count = first_page["total_count"]
    total_pages = max(1, math.ceil(total_count / PAGE_UNIT))

    list_items: List[Dict] = list(first_page["items"])
    for page_index in range(2, total_pages + 1):
        page = parse_list_page(page_index=page_index)
        list_items.extend(page["items"])
        time.sleep(0.2)

    output_rows = []
    for item in list_items:
        detail = parse_detail_item(
            ccba_kdcd=item["ccbaKdcd"],
            ccba_asno=item["ccbaAsno"],
            ccba_ctcd=item["ccbaCtcd"],
        )
        if detail["latitude"] and detail["longitude"]:
            output_rows.append(detail)
        time.sleep(0.1)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as outfile:
        json.dump(output_rows, outfile, ensure_ascii=False, indent=2)

    print(f"Processed {len(output_rows)} heritage records.")
    print(f"Wrote JSON: {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

import json
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
OUTPUT_PATH = PROJECT_ROOT / "index.html"

HERITAGE_PATH = PROJECT_ROOT / "locations" / "combined_heritage_sites.json"
VENUES_PATH = PROJECT_ROOT / "locations" / "venues.json"
SHRINES_PATH = PROJECT_ROOT / "locations" / "final_shrines.json"
SHRINE_IMAGES_DIR = PROJECT_ROOT / "shrine" / "images"

GOOGLE_MAPS_KEY_ENV = "GOOGLE_MAPS_API_KEY"


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


def read_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def build_shrine_image_map(images_dir: Path) -> dict[str, str]:
    if not images_dir.exists():
        return {}

    image_map: dict[str, str] = {}
    for path in sorted(images_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        shrine_id = path.stem.strip()
        if shrine_id:
            image_map[shrine_id] = f"shrine/images/{path.name}"
    return image_map


def main() -> int:
    load_env_file(ENV_PATH)
    google_maps_key = os.environ.get(GOOGLE_MAPS_KEY_ENV, "").strip()
    if not google_maps_key:
        raise RuntimeError(f"Missing required environment variable: {GOOGLE_MAPS_KEY_ENV}")

    heritage = read_json(HERITAGE_PATH)
    venues = read_json(VENUES_PATH)
    shrines = read_json(SHRINES_PATH)
    shrine_images = build_shrine_image_map(SHRINE_IMAGES_DIR)

    template = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>제5회 제주비엔날레 QR코드 매핑 전략 자료</title>
  <style>
    :root {
      --bg: #efe7d7;
      --panel: rgba(250, 245, 235, 0.96);
      --panel-border: rgba(80, 62, 41, 0.16);
      --text: #221b16;
      --muted: #6c5d4e;
      --accent: #0d6b78;
      --venue: #ffd60a;
      --shadow: 0 18px 40px rgba(43, 32, 20, 0.15);
      --radius: 18px;
      --header-h: 72px;
      --sidebar-w: 332px;
      --font: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: var(--font);
      color: var(--text);
      background:
        radial-gradient(circle at top left, rgba(12, 107, 120, 0.12), transparent 28%),
        radial-gradient(circle at bottom right, rgba(183, 127, 63, 0.18), transparent 24%),
        linear-gradient(180deg, #f4ecdc 0%, #e9deca 100%);
      min-height: 100vh;
      overflow: hidden;
    }

    .shell {
      display: grid;
      grid-template-rows: var(--header-h) 1fr;
      min-height: 100vh;
    }

    .header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 20px 0 18px;
      border-bottom: 1px solid rgba(60, 43, 24, 0.08);
      background: rgba(247, 241, 230, 0.94);
      backdrop-filter: blur(14px);
      position: sticky;
      top: 0;
      z-index: 40;
    }

    .header-title {
      display: flex;
      align-items: baseline;
      gap: 12px;
      flex-wrap: wrap;
    }

    .header-title h1 {
      margin: 0;
      font-size: 1.2rem;
      letter-spacing: -0.03em;
      font-weight: 800;
    }

    .header-title p {
      margin: 0;
      color: var(--muted);
      font-size: 0.92rem;
    }

    .header-meta {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .pill {
      border: 1px solid rgba(43, 32, 20, 0.08);
      background: rgba(255, 255, 255, 0.75);
      color: var(--muted);
      border-radius: 999px;
      padding: 7px 12px;
      font-size: 0.84rem;
      font-weight: 700;
    }

    .quick-filters {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    .quick-filter-group {
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }

    .quick-filter-group + .quick-filter-group {
      margin-left: 16px;
    }

    .quick-filter {
      border: 1px solid rgba(43, 32, 20, 0.08);
      background: rgba(255, 255, 255, 0.78);
      color: var(--text);
      border-radius: 999px;
      padding: 8px 12px;
      font: inherit;
      font-size: 0.84rem;
      font-weight: 700;
      cursor: pointer;
    }

    .quick-filter.is-active {
      color: white;
    }

    .quick-filter.filter-google.is-active {
      background: #3f4752;
      border-color: rgba(63, 71, 82, 0.42);
    }

    .quick-filter.filter-venues.is-active {
      background: var(--venue);
      color: #221b16;
      border-color: rgba(255, 214, 10, 0.5);
    }

    .quick-filter.filter-shrines.is-active {
      background: #cc6b2c;
      border-color: rgba(204, 107, 44, 0.45);
    }

    .quick-filter.filter-heritage.is-active {
      background: #7b5c3d;
      border-color: rgba(123, 92, 61, 0.45);
    }

    .toggle-button {
      display: none;
      border: 0;
      border-radius: 12px;
      background: var(--accent);
      color: white;
      padding: 10px 12px;
      font: inherit;
      font-weight: 700;
      box-shadow: var(--shadow);
    }

    .content {
      display: grid;
      grid-template-columns: var(--sidebar-w) 1fr;
      gap: 16px;
      padding: 16px;
      height: calc(100vh - var(--header-h));
      min-height: calc(100vh - var(--header-h));
      overflow: hidden;
    }

    .sidebar {
      background: var(--panel);
      border: 1px solid var(--panel-border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      overflow: hidden;
      display: flex;
      flex-direction: column;
      min-height: 0;
    }

    .sidebar-head {
      padding: 18px 18px 12px;
      border-bottom: 1px solid rgba(43, 32, 20, 0.08);
    }

    .sidebar-head h2 {
      margin: 0 0 6px;
      font-size: 1rem;
      letter-spacing: -0.03em;
    }

    .sidebar-head p {
      margin: 0;
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.45;
    }

    .sidebar-scroll {
      flex: 1 1 auto;
      overflow: auto;
      padding: 10px 10px 16px;
      min-height: 0;
    }

    details.section {
      background: rgba(255, 255, 255, 0.58);
      border: 1px solid rgba(43, 32, 20, 0.08);
      border-radius: 16px;
      margin: 8px 6px;
      overflow: hidden;
    }

    details.section[open] {
      background: rgba(255, 255, 255, 0.76);
    }

    details.section > summary {
      list-style: none;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 14px 16px;
      font-weight: 800;
      font-size: 0.96rem;
    }

    details.section > summary::-webkit-details-marker { display: none; }

    .summary-left {
      display: flex;
      align-items: center;
      gap: 10px;
      min-width: 0;
    }

    .summary-dot {
      width: 12px;
      height: 12px;
      border-radius: 999px;
      flex: 0 0 auto;
    }

    .summary-count {
      color: var(--muted);
      font-size: 0.84rem;
      font-weight: 700;
    }

    .section-body {
      padding: 0 16px 16px;
      display: grid;
      gap: 10px;
    }

    .section-note {
      color: var(--muted);
      font-size: 0.84rem;
      line-height: 1.45;
    }

    .master-toggle {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      padding: 12px 14px;
      background: rgba(13, 107, 120, 0.08);
      border-radius: 12px;
      font-size: 0.9rem;
      font-weight: 700;
    }

    .master-toggle input {
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
    }

    .route-toggle-button {
      border: 1px solid rgba(214, 40, 40, 0.18);
      background: rgba(214, 40, 40, 0.08);
      color: #8a1c1c;
      border-radius: 12px;
      padding: 12px 14px;
      font: inherit;
      font-size: 0.9rem;
      font-weight: 700;
      text-align: left;
      cursor: pointer;
      transition: background 0.2s ease, color 0.2s ease, border-color 0.2s ease;
    }

    .route-toggle-button.is-active {
      background: #d62828;
      border-color: rgba(214, 40, 40, 0.48);
      color: white;
    }

    .maptype-list {
      display: grid;
      gap: 8px;
    }

    .maptype-row {
      display: grid;
      grid-template-columns: 18px 1fr;
      align-items: center;
      gap: 10px;
      padding: 8px 4px;
      font-size: 0.9rem;
      cursor: pointer;
    }

    .maptype-row input {
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
    }

    .check-row {
      display: grid;
      grid-template-columns: 18px 14px 1fr auto;
      align-items: center;
      gap: 10px;
      padding: 8px 4px;
      font-size: 0.9rem;
    }

    .check-row input {
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
    }

    .swatch {
      width: 14px;
      height: 14px;
      border-radius: 999px;
      border: 1px solid rgba(43, 32, 20, 0.14);
    }

    .check-label {
      min-width: 0;
    }

    .check-count {
      color: var(--muted);
      font-size: 0.82rem;
      font-weight: 700;
    }

    .name-list {
      display: grid;
      gap: 6px;
    }

    .name-item {
      width: 100%;
      border: 1px solid rgba(43, 32, 20, 0.08);
      border-radius: 12px;
      background: rgba(255, 255, 255, 0.8);
      color: var(--text);
      font: inherit;
      text-align: left;
      padding: 10px 12px;
      cursor: pointer;
      line-height: 1.4;
    }

    .name-item:hover {
      background: rgba(255, 245, 196, 0.95);
    }

    details.meta-list {
      border: 1px dashed rgba(43, 32, 20, 0.12);
      border-radius: 12px;
      padding: 10px 12px;
    }

    details.meta-list > summary {
      cursor: pointer;
      font-size: 0.86rem;
      color: var(--muted);
      font-weight: 700;
    }

    .meta-items {
      display: grid;
      gap: 6px;
      margin-top: 10px;
    }

    .meta-item {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 0.84rem;
      color: var(--muted);
    }

    .map-card {
      position: relative;
      border-radius: calc(var(--radius) + 4px);
      overflow: hidden;
      box-shadow: var(--shadow);
      min-height: 0;
      height: 100%;
      background: #d7d2c9;
      border: 1px solid rgba(80, 62, 41, 0.12);
    }

    #map {
      width: 100%;
      height: 100%;
      min-height: 0;
    }

    .map-floating {
      position: absolute;
      left: 16px;
      bottom: 16px;
      display: grid;
      gap: 10px;
      width: min(320px, calc(100% - 32px));
      z-index: 5;
    }

    .floating-card {
      background: rgba(251, 248, 240, 0.95);
      border: 1px solid rgba(43, 32, 20, 0.08);
      border-radius: 16px;
      padding: 14px 15px;
      box-shadow: var(--shadow);
      backdrop-filter: blur(10px);
      display: grid;
      gap: 6px;
    }

    .floating-card strong {
      font-size: 0.92rem;
    }

    .floating-card span {
      font-size: 0.84rem;
      color: var(--muted);
      line-height: 1.5;
    }

    .focus-button {
      border: 0;
      border-radius: 14px;
      background: var(--accent);
      color: white;
      font: inherit;
      font-weight: 800;
      padding: 13px 16px;
      cursor: pointer;
      box-shadow: var(--shadow);
    }

    .custom-popup {
      width: min(340px, calc(100vw - 48px));
      max-width: 340px;
      padding: 0;
      margin: 0;
      overflow: visible;
      font-family: var(--font);
      color: var(--text);
    }

    .gm-style .gm-style-iw-c {
      padding: 0 !important;
      border-radius: 16px !important;
      background: transparent !important;
      box-shadow: none !important;
      max-width: none !important;
      overflow: visible !important;
    }

    .gm-style .gm-style-iw-d {
      overflow: visible !important;
      max-height: none !important;
    }

    .gm-style .gm-style-iw-tc {
      display: none !important;
    }

    .gm-style .gm-style-iw-ch {
      display: none !important;
    }

    .gm-style .gm-style-iw-chr {
      margin: 0;
    }

    .gm-style .gm-style-iw-ch button {
      display: none !important;
    }

    .popup-card {
      position: relative;
      overflow: visible;
      border-radius: 16px;
      background: rgba(251, 247, 239, 0.98);
      border: 1px solid rgba(43, 32, 20, 0.08);
      box-shadow: 0 16px 34px rgba(43, 32, 20, 0.2);
    }

    .popup-close {
      position: absolute;
      top: 12px;
      right: 12px;
      width: 30px;
      height: 30px;
      border: 0;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.9);
      color: #3e3328;
      font: inherit;
      font-size: 1rem;
      font-weight: 800;
      line-height: 1;
      cursor: pointer;
      box-shadow: 0 8px 18px rgba(43, 32, 20, 0.16);
      z-index: 3;
    }

    .popup-image {
      display: block;
      width: 100%;
      height: 148px;
      object-fit: cover;
      background: #ddd6ca;
      border-radius: 12px;
    }

    .popup-body {
      padding: 22px 56px 24px 22px;
      display: grid;
      gap: 14px;
    }

    .popup-title {
      margin: 0;
      font-size: 1rem;
      line-height: 1.4;
    }

    .popup-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 5px 9px;
      background: rgba(13, 107, 120, 0.08);
      font-size: 0.78rem;
      font-weight: 700;
      color: var(--muted);
    }

    .popup-text,
    .popup-address {
      font-size: 0.86rem;
      line-height: 1.55;
      color: #40362d;
    }

    .popup-text details summary {
      cursor: pointer;
      font-weight: 700;
      color: var(--accent);
      margin-bottom: 6px;
    }

    .popup-description summary {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      border-radius: 999px;
      padding: 7px 11px;
      background: rgba(13, 107, 120, 0.08);
      font-size: 0.8rem;
      font-weight: 800;
      color: var(--accent);
    }

    .popup-sidecard {
      display: none;
      position: absolute;
      top: 0;
      left: calc(100% + 10px);
      width: min(340px, calc(100vw - 64px));
      max-height: min(62vh, 520px);
      overflow: hidden;
      border-radius: 16px;
      background: rgba(251, 247, 239, 0.98);
      border: 1px solid rgba(43, 32, 20, 0.08);
      box-shadow: 0 16px 34px rgba(43, 32, 20, 0.2);
      padding: 18px 18px 20px;
      z-index: 4;
    }

    .popup-sidecard-open {
      display: block;
    }

    .popup-description details[open] .popup-sidecard {
      display: block;
    }

    .popup-sidecard-title {
      margin: 0 0 10px;
      font-size: 0.92rem;
      font-weight: 800;
      color: var(--text);
    }

    .popup-sidecard-text {
      max-height: min(48vh, 420px);
      overflow-y: auto;
      padding-right: 8px;
      font-size: 0.86rem;
      line-height: 1.62;
      color: #40362d;
      white-space: pre-wrap;
    }

    .popup-sidecard-close {
      position: absolute;
      top: 12px;
      right: 12px;
      width: 28px;
      height: 28px;
      border: 0;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: rgba(255, 255, 255, 0.92);
      color: #3e3328;
      font: inherit;
      font-size: 0.98rem;
      font-weight: 800;
      line-height: 1;
      cursor: pointer;
      box-shadow: 0 8px 18px rgba(43, 32, 20, 0.16);
      z-index: 2;
    }

    .popup-sidecard-image {
      padding-top: 46px;
    }

    .popup-sidecard-image img {
      display: block;
      width: 100%;
      max-height: min(48vh, 420px);
      object-fit: contain;
      border-radius: 12px;
      background: #ddd6ca;
    }

    .map-error {
      width: 100%;
      height: 100%;
      min-height: 640px;
      display: grid;
      place-items: center;
      padding: 24px;
      text-align: center;
      color: #5c4a39;
      font-weight: 700;
      line-height: 1.6;
      background: #f3eee4;
    }

    @media (max-width: 980px) {
      .toggle-button {
        display: inline-flex;
      }

      .content {
        grid-template-columns: 1fr;
      }

      .sidebar {
        position: fixed;
        top: calc(var(--header-h) + 10px);
        left: 16px;
        width: min(calc(100vw - 32px), 360px);
        max-height: calc(100vh - var(--header-h) - 26px);
        z-index: 80;
        transform: translateX(-120%);
        transition: transform 0.22s ease;
      }

      .sidebar.open {
        transform: translateX(0);
      }

      .map-card,
      #map {
        min-height: calc(100vh - var(--header-h) - 32px);
      }

      .header {
        padding-inline: 14px;
      }

      .header-meta .pill {
        display: none;
      }

      .popup-sidecard {
        position: static;
        width: 100%;
        max-height: 240px;
        margin-top: 12px;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <header class="header">
      <div class="header-title">
        <h1>제5회 제주비엔날레 QR코드 매핑 전략 자료</h1>
        <p>제공 SKOR Lab 김희은</p>
      </div>
      <div class="header-meta">
        <div class="quick-filters">
          <div class="quick-filter-group">
            <button class="quick-filter filter-google" id="toggleGooglePoiButton" type="button">지도 랜드마크</button>
          </div>
          <div class="quick-filter-group">
            <button class="quick-filter filter-venues" id="showVenuesOnlyButton" type="button">비엔날레 베뉴</button>
            <button class="quick-filter filter-shrines" id="showShrinesOnlyButton" type="button">신당</button>
            <button class="quick-filter filter-heritage" id="showHeritageOnlyButton" type="button">문화유산</button>
          </div>
        </div>
        <span class="pill" id="header-counts">레이어 로딩 중</span>
        <button class="toggle-button" id="sidebarToggle" type="button">필터</button>
      </div>
    </header>

    <div class="content">
      <aside class="sidebar" id="sidebar">
        <div class="sidebar-head">
          <h2>레이어 제어</h2>
          <p>비엔날레 베뉴, 신당, 문화유산 레이어를 한 화면에서 비교합니다. 신당 위치 정보는 2017년 제주학연구센터 연구논문 <a href="http://jst.re.kr/upload/pdf/RC00085041.pdf" target="_blank" rel="noopener noreferrer">「제주 신당의 공공자원화를 위한 기초조사」</a>(김석윤, 송정희, 이재섭) 자료를 바탕으로 제작되었습니다.</p>
        </div>
        <div class="sidebar-scroll">
          <details class="section" open id="basemapSection">
            <summary>
              <div class="summary-left">
                <span class="summary-dot" style="background:#3f4752;"></span>
                <span>기본 지도</span>
              </div>
              <span class="summary-count">Google</span>
            </summary>
            <div class="section-body">
              <div class="maptype-list">
                <label class="maptype-row">
                  <input type="radio" name="mapType" value="roadmap" checked />
                  <span>기본</span>
                </label>
                <label class="maptype-row">
                  <input type="radio" name="mapType" value="hybrid" />
                  <span>하이브리드</span>
                </label>
              </div>
              <label class="master-toggle">
                <span>지도 랜드마크 표시</span>
                <input type="checkbox" id="googlePoiToggle" checked />
              </label>
              <p class="section-note">지도 유형은 전환해서 비교할 수 있고, Street View는 지도 오른쪽 하단의 기본 컨트롤에서 바로 열 수 있습니다.</p>
            </div>
          </details>

          <details class="section" open id="venuesSection">
            <summary>
              <div class="summary-left">
                <span class="summary-dot" style="background:var(--venue);"></span>
                <span>비엔날레 베뉴</span>
              </div>
              <span class="summary-count" id="venuesTotalCount"></span>
            </summary>
            <div class="section-body">
              <label class="master-toggle">
                <span>전체 표시</span>
                <input type="checkbox" id="venuesMasterToggle" checked />
              </label>
              <div id="venueNameList" class="name-list"></div>
              <button class="route-toggle-button" id="venueRouteToggle" type="button">동선 표시</button>
              <p class="section-note">도로망을 따라 각 비엔날레 베뉴를 연결한 동선을 빨간 선으로 표시합니다.</p>
            </div>
          </details>

          <details class="section" open id="shrinesSection">
            <summary>
              <div class="summary-left">
                <span class="summary-dot" style="background:#cc6b2c;"></span>
                <span>신당</span>
              </div>
              <span class="summary-count" id="shrinesTotalCount"></span>
            </summary>
            <div class="section-body">
              <label class="master-toggle">
                <span>전체 표시</span>
                <input type="checkbox" id="shrinesMasterToggle" checked />
              </label>
              <div id="shrineOwnerList"></div>
              <div id="shrineStatusList"></div>
              <p class="section-note" id="shrineNoCoordNote"></p>
            </div>
          </details>

          <details class="section" open id="heritageSection">
            <summary>
              <div class="summary-left">
                <span class="summary-dot" style="background:#7b5c3d;"></span>
                <span>문화유산</span>
              </div>
              <span class="summary-count" id="heritageTotalCount"></span>
            </summary>
            <div class="section-body">
              <label class="master-toggle">
                <span>전체 표시</span>
                <input type="checkbox" id="heritageMasterToggle" checked />
              </label>
              <div id="heritageTypeList"></div>
              <details class="meta-list">
                <summary>유산 객체 유형 보기</summary>
                <div class="meta-items" id="heritageGcodeList"></div>
              </details>
            </div>
          </details>
        </div>
      </aside>

      <section class="map-card">
        <div id="map"></div>
        <div class="map-floating">
          <div class="floating-card" id="focusInfoCard">
            <strong>제주원도심 포커스 영역</strong>
            <span>관덕정 일대를 기준으로 시작하며, 청록색 외곽선은 현재 인터페이스의 집중 관찰 구간입니다.</span>
          </div>
          <button class="focus-button" id="focusButton" type="button">원도심 포커스</button>
        </div>
      </section>
    </div>
  </div>

  <script>
    window.__MAP_DATA__ = {
      heritage: __HERITAGE_DATA__,
      venues: __VENUE_DATA__,
      shrines: __SHRINE_DATA__
    };
  </script>
  <script>
    const mapData = window.__MAP_DATA__;
    const shrineImageMap = __SHRINE_IMAGE_MAP_JSON__;
    const googleMapsApiKey = "__GOOGLE_MAPS_API_KEY__";
    const venueRouteDataPromise = fetch("locations/venue-route.json")
      .then((response) => {
        if (!response.ok) {
          throw new Error(`Failed to load venue route data: ${response.status}`);
        }
        return response.json();
      })
      .catch((error) => {
        console.warn("Failed to load local venue route data.", error);
        return { legs: [] };
      });
    const focusBoundsLiteral = {
      north: 33.535,
      south: 33.490,
      east: 126.560,
      west: 126.490
    };

    const jejuBoundsLiteral = {
      north: 33.62,
      south: 33.10,
      east: 126.98,
      west: 126.08
    };

    const focusCenterLiteral = { lat: 33.5100, lng: 126.5216 };

    const heritagePalette = {
      "보물": "#ff7a18",
      "사적": "#ff4d6d",
      "천연기념물": "#32d17c",
      "국가민속문화유산": "#ff66cc",
      "명승": "#00c2ff",
      "시도기념물": "#ffb703",
      "시도유형문화유산": "#7b61ff",
      "시도민속문화유산": "#ff8c42",
      "문화유산자료": "#5ac8fa",
      "국가등록문화유산": "#00b894",
      "기타": "#9aa0a6"
    };

    const shrinePalette = {
      "국가": "#ff3b30",
      "개인": "#ff9500",
      "공동": "#ffd60a",
      "법인": "#bf5af2",
      "미상": "#8e8e93"
    };

    const state = {
      sections: {
        heritage: true,
        venues: true,
        shrines: true
      },
      heritageTypes: new Set(),
      shrineOwners: new Set(),
      includeClosedShrines: true,
      markers: {
        heritage: [],
        venues: [],
        shrines: []
      },
      popup: null,
      focusMode: false,
      googlePoiVisible: true,
      mapTypeId: "roadmap",
      venueRouteVisible: false
    };

    let map;
    let focusRectangle;
    let venueRoutePolyline;

    window.__closeMapPopup = function closeMapPopup() {
      if (state.popup) {
        state.popup.close();
      }
    };

    function normalizeHeritageType(value) {
      return value || "기타";
    }

    function countBy(items, getKey) {
      const counts = new Map();
      items.forEach((item) => {
        const key = getKey(item);
        counts.set(key, (counts.get(key) || 0) + 1);
      });
      return [...counts.entries()].sort((a, b) => b[1] - a[1]);
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function createSvgMarker(shape, color, size, options = {}) {
      const isClosed = Boolean(options.isClosed);
      let svg = "";
      if (shape === "diamond") {
        svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 40 40"><rect x="8" y="8" width="24" height="24" rx="4" transform="rotate(45 20 20)" fill="${color}" stroke="rgba(34,27,22,0.68)" stroke-width="1.6"/></svg>`;
      } else if (shape === "star") {
        svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 40 40"><path d="M20 3.5l4.9 10 11 1.6-7.9 7.7 1.9 10.9L20 28.5l-9.9 5.2 1.9-10.9-7.9-7.7 11-1.6z" fill="${color}" stroke="rgba(34,27,22,0.62)" stroke-width="1.4"/></svg>`;
      } else if (shape === "shrine") {
        const closedOverlay = isClosed
          ? `<path d="M10 30 L30 10" stroke="rgba(34,27,22,0.92)" stroke-width="4.2" stroke-linecap="round"/><path d="M10 30 L30 10" stroke="rgba(255,255,255,0.96)" stroke-width="2.1" stroke-linecap="round"/>`
          : "";
        svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 40 40"><path d="M20 3.5c6.8 0 12.3 5.4 12.3 12.1 0 8.8-8.8 13.3-12.3 20.9-3.5-7.6-12.3-12.1-12.3-20.9C7.7 8.9 13.2 3.5 20 3.5z" fill="${color}" stroke="rgba(34,27,22,0.68)" stroke-width="1.5"/><path d="M12.5 16.5h15" stroke="rgba(255,255,255,0.9)" stroke-width="1.6" stroke-linecap="round"/><path d="M15 12.8h10" stroke="rgba(255,255,255,0.85)" stroke-width="1.4" stroke-linecap="round"/><path d="M20 11.5v10.5" stroke="rgba(255,255,255,0.85)" stroke-width="1.4" stroke-linecap="round"/>${closedOverlay}</svg>`;
      } else {
        svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 40 40"><circle cx="20" cy="20" r="11" fill="${color}" stroke="rgba(34,27,22,0.58)" stroke-width="1.4"/></svg>`;
      }
      return "data:image/svg+xml;charset=UTF-8," + encodeURIComponent(svg);
    }

    function setPopup(marker, html) {
      marker.addListener("click", () => {
        if (state.popup) {
          state.popup.close();
        }
        state.popup = new google.maps.InfoWindow({
          headerDisabled: true,
          content: `<div class="custom-popup">${html}</div>`
        });
        state.popup.open({ map, anchor: marker });
      });
    }

    function buildPopupCard({ title, badges = [], image = null, body = "", footer = "", sidecard = "" }) {
      const badgesHtml = badges
        .filter(Boolean)
        .map((badge) => `<span class="badge ${badge.className || ""}">${escapeHtml(badge.label)}</span>`)
        .join("");
      const imageHtml = image ? `<img class="popup-image" src="${escapeHtml(image)}" alt="${escapeHtml(title)}" />` : "";
      return `
        <div class="popup-card">
          <button class="popup-close" type="button" aria-label="닫기" onclick="window.__closeMapPopup && window.__closeMapPopup()">&times;</button>
          <div class="popup-body">
            ${imageHtml}
            <h3 class="popup-title">${escapeHtml(title)}</h3>
            <div class="popup-meta">${badgesHtml}</div>
            ${body}
            ${footer}
          </div>
          ${sidecard}
        </div>
      `;
    }

    function heritageBody(item) {
      return item.description
        ? `<div class="popup-text popup-description"><details><summary>설명 펼치기</summary><div class="popup-sidecard"><h4 class="popup-sidecard-title">설명</h4><div class="popup-sidecard-text">${escapeHtml(item.description)}</div></div></details></div>`
        : `<div class="popup-text">설명 정보 없음</div>`;
    }

    function shrineSourceStatus(item) {
      return item["상태"] || "";
    }

    function shrineImagePath(item) {
      const shrineId = String(item.ID || "").trim();
      return shrineImageMap[shrineId] || "";
    }

    function buildShrineImageSidecard(item) {
      const imagePath = shrineImagePath(item);
      if (!imagePath) {
        return "";
      }
      const shrineId = String(item.ID || "").trim();
      const sidecardTitle = shrineId ? `신당 이미지 · ID ${shrineId}` : "신당 이미지";
      return `
        <div class="popup-sidecard popup-sidecard-open popup-sidecard-image">
          <button class="popup-sidecard-close" type="button" aria-label="이미지 닫기" onclick="this.closest('.popup-sidecard').style.display='none'">&times;</button>
          <h4 class="popup-sidecard-title">${escapeHtml(sidecardTitle)}</h4>
          <img src="${escapeHtml(imagePath)}" alt="${escapeHtml(item.shrine_name || sidecardTitle)}" loading="lazy" />
        </div>
      `;
    }

    function shrineBody(item) {
      const shrineId = item.ID || "ID 없음";
      const address = item.validated_address_ko || "주소 정보 없음";
      const confidence = item.validated_address_ko ? "좌표 검증 주소" : "주소 미검증";
      const sourceStatus = shrineSourceStatus(item);
      const statusHtml = sourceStatus
        ? `<span class="badge">${escapeHtml(`상태: ${sourceStatus}`)}</span>`
        : "";
      return `
        <div class="popup-text">ID ${escapeHtml(shrineId)}</div>
        <div class="popup-address">${escapeHtml(address)}</div>
        <div class="popup-meta">
          ${statusHtml}
          <span class="badge">${escapeHtml(confidence)}</span>
        </div>
      `;
    }

    function venueBody() {
      return `<div class="popup-text">비엔날레 장소</div>`;
    }

    function createMarker(shape, color, size, position, title, options = {}) {
      return new google.maps.Marker({
        position,
        map,
        title,
        icon: {
          url: createSvgMarker(shape, color, size, options),
          scaledSize: new google.maps.Size(size, size),
          anchor: new google.maps.Point(size / 2, size / 2)
        }
      });
    }

    function isWithinFocusBounds(marker) {
      const position = marker.getPosition();
      if (!position) return false;
      const lat = position.lat();
      const lng = position.lng();
      return (
        lat >= focusBoundsLiteral.south &&
        lat <= focusBoundsLiteral.north &&
        lng >= focusBoundsLiteral.west &&
        lng <= focusBoundsLiteral.east
      );
    }

    function createHeritageMarkers() {
      mapData.heritage.forEach((item) => {
        const heritageType = normalizeHeritageType(item.ccmaName);
        const color = heritagePalette[heritageType] || heritagePalette["기타"];
        const position = {
          lat: Number(item.latitude),
          lng: Number(item.longitude)
        };
        const marker = createMarker("diamond", color, 22, position, item.name);
        setPopup(marker, buildPopupCard({
          title: item.name,
          image: item.image,
          badges: [
            { label: heritageType, className: "heritage-type" },
            item.gcodeName ? { label: item.gcodeName } : null
          ],
          body: heritageBody(item)
        }));
        state.markers.heritage.push({ marker, type: heritageType });
      });
    }

    function createVenueMarkers() {
      mapData.venues.forEach((item) => {
        const position = {
          lat: Number(item.latitude),
          lng: Number(item.longitude)
        };
        const marker = createMarker("star", "#ffd60a", 38, position, item.name);
        setPopup(marker, buildPopupCard({
          title: item.name,
          badges: [{ label: "비엔날레 베뉴" }],
          body: venueBody()
        }));
        state.markers.venues.push({ marker, item });
      });
    }

    function buildVenueRoute() {
      if (!map || mapData.venues.length < 2 || !google.maps.Polyline) {
        return;
      }

      venueRoutePolyline = new google.maps.Polyline({
        geodesic: false,
        strokeColor: "#d62828",
        strokeOpacity: 0.95,
        strokeWeight: 5,
        map: null
      });

      venueRouteDataPromise.then((routeData) => {
        const combinedPath = Array.isArray(routeData.legs)
          ? routeData.legs.flatMap((leg, legIndex) => (
              Array.isArray(leg.path)
                ? leg.path.filter((point, pointIndex) => (
                    Number.isFinite(point.lat) &&
                    Number.isFinite(point.lng) &&
                    !(legIndex > 0 && pointIndex === 0)
                  ))
                : []
            ))
          : [];

        if (!combinedPath.length) {
          console.warn("No local venue route data was available to draw.");
          if (venueRoutePolyline) {
            venueRoutePolyline.setMap(null);
            venueRoutePolyline = null;
          }
          updateVenueRouteButton();
          return;
        }

        venueRoutePolyline.setPath(combinedPath);
        updateVenueRouteVisibility();
      });
    }

    function createShrineMarkers() {
      mapData.shrines
        .filter((item) => item.latitude && item.longitude)
        .forEach((item) => {
          const owner = item.ownership_standardized || "미상";
          const sourceStatus = shrineSourceStatus(item);
          const isClosed = sourceStatus === "폐당";
          const color = shrinePalette[owner] || shrinePalette["미상"];
          const position = {
            lat: Number(item.latitude),
            lng: Number(item.longitude)
          };
          const marker = createMarker("shrine", color, 28, position, item.shrine_name, { isClosed });
          setPopup(marker, buildPopupCard({
            title: item.shrine_name,
            badges: [{ label: owner }],
            body: shrineBody(item),
            sidecard: buildShrineImageSidecard(item)
          }));
          state.markers.shrines.push({ marker, owner, isClosed });
        });
    }

    function updateVenueRouteVisibility() {
      if (!venueRoutePolyline) {
        updateVenueRouteButton();
        return;
      }

      const shouldShowRoute = state.sections.venues && state.venueRouteVisible;
      venueRoutePolyline.setMap(shouldShowRoute ? map : null);
      updateVenueRouteButton();
    }

    function updateVenueRouteButton() {
      const button = document.getElementById("venueRouteToggle");
      if (!button) {
        return;
      }
      button.classList.toggle("is-active", state.venueRouteVisible);
    }

    function refreshMarkerVisibility() {
      state.markers.heritage.forEach(({ marker, type }) => {
        const visible = (
          state.sections.heritage &&
          state.heritageTypes.has(type) &&
          (!state.focusMode || isWithinFocusBounds(marker))
        );
        marker.setMap(visible ? map : null);
      });
      state.markers.venues.forEach(({ marker }) => {
        const visible = state.sections.venues;
        marker.setMap(visible ? map : null);
      });
      state.markers.shrines.forEach(({ marker, owner, isClosed }) => {
        const visible = (
          state.sections.shrines &&
          state.shrineOwners.has(owner) &&
          (state.includeClosedShrines || !isClosed) &&
          (!state.focusMode || isWithinFocusBounds(marker))
        );
        marker.setMap(visible ? map : null);
      });
      updateVenueRouteVisibility();
      updateTopFilterButtons();
    }

    function updateTopFilterButtons() {
      const activeSectionName = state.sections.venues && !state.sections.shrines && !state.sections.heritage
        ? "venues"
        : state.sections.shrines && !state.sections.venues && !state.sections.heritage
          ? "shrines"
          : state.sections.heritage && !state.sections.venues && !state.sections.shrines
            ? "heritage"
            : null;

      const buttonMap = {
        venues: document.getElementById("showVenuesOnlyButton"),
        shrines: document.getElementById("showShrinesOnlyButton"),
        heritage: document.getElementById("showHeritageOnlyButton")
      };

      Object.entries(buttonMap).forEach(([sectionName, button]) => {
        if (!button) {
          return;
        }
        button.classList.toggle("is-active", activeSectionName === sectionName);
      });

      const googlePoiButton = document.getElementById("toggleGooglePoiButton");
      if (googlePoiButton) {
        googlePoiButton.classList.toggle("is-active", state.googlePoiVisible);
      }
    }

    function syncSectionMasterToggles() {
      const heritageToggle = document.getElementById("heritageMasterToggle");
      const venuesToggle = document.getElementById("venuesMasterToggle");
      const shrinesToggle = document.getElementById("shrinesMasterToggle");

      if (heritageToggle) {
        heritageToggle.checked = state.sections.heritage;
        heritageToggle.indeterminate = false;
      }
      if (venuesToggle) {
        venuesToggle.checked = state.sections.venues;
        venuesToggle.indeterminate = false;
      }
      if (shrinesToggle) {
        shrinesToggle.checked = state.sections.shrines;
        shrinesToggle.indeterminate = false;
      }
    }

    function showOnlySection(sectionName) {
      state.sections.heritage = sectionName === "heritage";
      state.sections.venues = sectionName === "venues";
      state.sections.shrines = sectionName === "shrines";
      syncSectionMasterToggles();
      refreshMarkerVisibility();
    }

    function createCheckRow({ id, label, count, color, checked, onChange }) {
      const row = document.createElement("label");
      row.className = "check-row";
      row.innerHTML = `
        <input id="${id}" type="checkbox" ${checked ? "checked" : ""} />
        <span class="swatch" style="background:${color};"></span>
        <span class="check-label">${escapeHtml(label)}</span>
        <span class="check-count">${count}</span>
      `;
      row.querySelector("input").addEventListener("change", onChange);
      return row;
    }

    function renderSidebar() {
      const heritageTypes = countBy(mapData.heritage, (item) => normalizeHeritageType(item.ccmaName));
      const heritageGcodes = countBy(mapData.heritage, (item) => item.gcodeName || "기타");
      const shrineOwners = countBy(
        mapData.shrines.filter((item) => item.latitude && item.longitude),
        (item) => item.ownership_standardized || "미상"
      );
      const closedShrines = mapData.shrines.filter((item) => (
        item.latitude &&
        item.longitude &&
        shrineSourceStatus(item) === "폐당"
      )).length;
      const shrineNoCoords = mapData.shrines.filter((item) => !item.latitude || !item.longitude).length;

      heritageTypes.forEach(([type]) => state.heritageTypes.add(type));
      shrineOwners.forEach(([owner]) => state.shrineOwners.add(owner));

      document.getElementById("heritageTotalCount").textContent = `${mapData.heritage.length}건`;
      document.getElementById("venuesTotalCount").textContent = `${mapData.venues.length}곳`;
      document.getElementById("shrinesTotalCount").textContent = `${mapData.shrines.length}건`;
      document.getElementById("header-counts").textContent = `문화유산 ${mapData.heritage.length} · 베뉴 ${mapData.venues.length} · 신당 ${mapData.shrines.length}`;
      document.getElementById("shrineNoCoordNote").textContent = `좌표 없음 ${shrineNoCoords}건은 지도에서 숨김 처리했습니다.`;

      const heritageList = document.getElementById("heritageTypeList");
      heritageTypes.forEach(([type, count]) => {
        heritageList.appendChild(createCheckRow({
          id: `heritage-${type}`,
          label: type,
          count,
          color: heritagePalette[type] || heritagePalette["기타"],
          checked: true,
          onChange: (event) => {
            if (event.target.checked) {
              state.heritageTypes.add(type);
            } else {
              state.heritageTypes.delete(type);
            }
            state.sections.heritage = state.heritageTypes.size > 0;
            syncMasterToggle("heritage");
            refreshMarkerVisibility();
          }
        }));
      });

      const heritageGcodeList = document.getElementById("heritageGcodeList");
      heritageGcodes.forEach(([gcode, count]) => {
        const item = document.createElement("div");
        item.className = "meta-item";
        item.innerHTML = `<span>${escapeHtml(gcode)}</span><span>${count}</span>`;
        heritageGcodeList.appendChild(item);
      });

      const shrineOwnerList = document.getElementById("shrineOwnerList");
      shrineOwners.forEach(([owner, count]) => {
        shrineOwnerList.appendChild(createCheckRow({
          id: `shrine-${owner}`,
          label: owner,
          count,
          color: shrinePalette[owner] || shrinePalette["미상"],
          checked: true,
          onChange: (event) => {
            if (event.target.checked) {
              state.shrineOwners.add(owner);
            } else {
              state.shrineOwners.delete(owner);
            }
            state.sections.shrines = state.shrineOwners.size > 0;
            syncMasterToggle("shrines");
            refreshMarkerVisibility();
          }
        }));
      });

      const shrineStatusList = document.getElementById("shrineStatusList");
      shrineStatusList.appendChild(createCheckRow({
        id: "shrine-status-closed",
        label: "폐당",
        count: closedShrines,
        color: "#ffffff",
        checked: true,
        onChange: (event) => {
          state.includeClosedShrines = event.target.checked;
          syncMasterToggle("shrines");
          refreshMarkerVisibility();
        }
      }));

      const venueNameList = document.getElementById("venueNameList");
      mapData.venues.forEach((venue) => {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "name-item";
        button.textContent = venue.name;
        button.addEventListener("click", () => {
          state.focusMode = false;
          refreshMarkerVisibility();
          map.panTo({ lat: Number(venue.latitude), lng: Number(venue.longitude) });
          map.setZoom(14);
        });
        venueNameList.appendChild(button);
      });

      document.getElementById("heritageMasterToggle").addEventListener("change", (event) => {
        state.sections.heritage = event.target.checked;
        const allTypes = countBy(mapData.heritage, (item) => normalizeHeritageType(item.ccmaName)).map(([type]) => type);
        state.heritageTypes = event.target.checked ? new Set(allTypes) : new Set();
        event.target.indeterminate = false;
        allTypes.forEach((type) => {
          const input = document.getElementById(`heritage-${type}`);
          if (input) {
            input.checked = event.target.checked;
          }
        });
        refreshMarkerVisibility();
      });
      document.getElementById("venuesMasterToggle").addEventListener("change", (event) => {
        state.sections.venues = event.target.checked;
        refreshMarkerVisibility();
      });
      const venueRouteToggle = document.getElementById("venueRouteToggle");
      if (venueRouteToggle) {
        venueRouteToggle.addEventListener("click", () => {
          state.venueRouteVisible = !state.venueRouteVisible;
          updateVenueRouteVisibility();
        });
      }
      document.getElementById("shrinesMasterToggle").addEventListener("change", (event) => {
        state.sections.shrines = event.target.checked;
        const allOwners = countBy(
          mapData.shrines.filter((item) => item.latitude && item.longitude),
          (item) => item.ownership_standardized || "미상"
        ).map(([owner]) => owner);
        state.shrineOwners = event.target.checked ? new Set(allOwners) : new Set();
        state.includeClosedShrines = event.target.checked;
        event.target.indeterminate = false;
        allOwners.forEach((owner) => {
          const input = document.getElementById(`shrine-${owner}`);
          if (input) {
            input.checked = event.target.checked;
          }
        });
        const closedInput = document.getElementById("shrine-status-closed");
        if (closedInput) {
          closedInput.checked = event.target.checked;
        }
        refreshMarkerVisibility();
      });
      updateVenueRouteButton();
    }

    function syncMasterToggle(sectionName) {
      if (sectionName === "heritage") {
        const allTypes = countBy(mapData.heritage, (item) => normalizeHeritageType(item.ccmaName)).map(([type]) => type);
        const toggle = document.getElementById("heritageMasterToggle");
        toggle.checked = allTypes.every((type) => state.heritageTypes.has(type));
        toggle.indeterminate = state.heritageTypes.size > 0 && state.heritageTypes.size < allTypes.length;
      } else if (sectionName === "shrines") {
        const allOwners = countBy(
          mapData.shrines.filter((item) => item.latitude && item.longitude),
          (item) => item.ownership_standardized || "미상"
        ).map(([owner]) => owner);
        const toggle = document.getElementById("shrinesMasterToggle");
        const ownersComplete = allOwners.every((owner) => state.shrineOwners.has(owner));
        toggle.checked = ownersComplete && state.includeClosedShrines;
        toggle.indeterminate = (
          (state.shrineOwners.size > 0 && state.shrineOwners.size < allOwners.length) ||
          (ownersComplete && !state.includeClosedShrines)
        );
      }
    }

    function bindUi() {
      document.getElementById("focusButton").addEventListener("click", () => {
        const button = document.getElementById("focusButton");
        state.focusMode = !state.focusMode;
        const infoCard = document.getElementById("focusInfoCard");

        if (state.focusMode) {
          if (infoCard) {
            infoCard.style.display = "none";
          }
          if (focusRectangle) {
            focusRectangle.setMap(map);
          }
          if (button) {
            button.textContent = "ì „ì²´";
          }
        } else {
          if (infoCard) {
            infoCard.style.display = "";
          }
          if (focusRectangle) {
            focusRectangle.setMap(null);
          }
          if (button) {
            button.textContent = "ì›ë„ì‹¬ í¬ì»¤ìŠ¤";
          }
        }

        refreshMarkerVisibility();
      });

      document.getElementById("sidebarToggle").addEventListener("click", () => {
        document.getElementById("sidebar").classList.toggle("open");
      });

      const venuesOnlyButton = document.getElementById("showVenuesOnlyButton");
      if (venuesOnlyButton) {
        venuesOnlyButton.addEventListener("click", () => {
          showOnlySection("venues");
        });
      }

      const shrinesOnlyButton = document.getElementById("showShrinesOnlyButton");
      if (shrinesOnlyButton) {
        shrinesOnlyButton.addEventListener("click", () => {
          showOnlySection("shrines");
        });
      }

      const heritageOnlyButton = document.getElementById("showHeritageOnlyButton");
      if (heritageOnlyButton) {
        heritageOnlyButton.addEventListener("click", () => {
          showOnlySection("heritage");
        });
      }

      const googlePoiButton = document.getElementById("toggleGooglePoiButton");
      if (googlePoiButton) {
        googlePoiButton.addEventListener("click", () => {
          state.googlePoiVisible = !state.googlePoiVisible;
          const googlePoiToggle = document.getElementById("googlePoiToggle");
          if (googlePoiToggle) {
            googlePoiToggle.checked = state.googlePoiVisible;
          }
          applyBaseMapStyle();
          updateTopFilterButtons();
        });
      }

      document.getElementById("googlePoiToggle").addEventListener("change", (event) => {
        state.googlePoiVisible = event.target.checked;
        applyBaseMapStyle();
        updateTopFilterButtons();
      });

      document.querySelectorAll('input[name="mapType"]').forEach((input) => {
        input.addEventListener("change", (event) => {
          if (!event.target.checked) {
            return;
          }

          state.mapTypeId = event.target.value;
          if (map) {
            map.setMapTypeId(state.mapTypeId);
          }
        });
      });

    }

    function applyBaseMapStyle() {
      if (!map) return;
      if (state.googlePoiVisible) {
        map.setOptions({ styles: [] });
        return;
      }
      map.setOptions({
        styles: [
          {
            featureType: "poi",
            elementType: "all",
            stylers: [{ visibility: "off" }]
          },
          {
            featureType: "transit.station",
            elementType: "all",
            stylers: [{ visibility: "off" }]
          },
          {
            featureType: "road",
            elementType: "labels.icon",
            stylers: [{ visibility: "off" }]
          },
          {
            featureType: "road.highway",
            elementType: "labels",
            stylers: [{ visibility: "off" }]
          }
        ]
      });
    }

    function showMapError(message) {
      const container = document.getElementById("map");
      container.innerHTML = `<div class="map-error">${escapeHtml(message)}</div>`;
    }

    function initializeMap() {
      map = new google.maps.Map(document.getElementById("map"), {
        center: focusCenterLiteral,
        zoom: 11,
        mapTypeId: state.mapTypeId,
        minZoom: 8,
        maxZoom: 17,
        restriction: {
          latLngBounds: jejuBoundsLiteral,
          strictBounds: false
        },
        mapTypeControl: false,
        streetViewControl: true,
        fullscreenControl: false
      });

      focusRectangle = new google.maps.Rectangle({
        bounds: focusBoundsLiteral,
        strokeColor: "#0c6b78",
        strokeOpacity: 1,
        strokeWeight: 2,
        fillColor: "#0c6b78",
        fillOpacity: 0,
        map: null
      });

      createHeritageMarkers();
      createVenueMarkers();
      createShrineMarkers();
      buildVenueRoute();
      renderSidebar();
      applyBaseMapStyle();
      refreshMarkerVisibility();
      bindUi();
    }

    function loadGoogleMapsApi() {
      const script = document.createElement("script");
      script.src = `https://maps.googleapis.com/maps/api/js?key=${googleMapsApiKey}&language=ko&region=KR&callback=initMap`;
      script.async = true;
      script.defer = true;
      script.onerror = () => {
        showMapError("Google Maps JavaScript API failed to load. Check the API key, billing state, and allowed referrers.");
      };
      document.head.appendChild(script);
    }

    window.initMap = initializeMap;
    loadGoogleMapsApi();
  </script>
</body>
</html>
"""

    html = (
        template.replace("__GOOGLE_MAPS_API_KEY__", google_maps_key)
        .replace("__HERITAGE_DATA__", json.dumps(heritage, ensure_ascii=False))
        .replace("__VENUE_DATA__", json.dumps(venues, ensure_ascii=False))
        .replace("__SHRINE_DATA__", json.dumps(shrines, ensure_ascii=False))
        .replace("__SHRINE_IMAGE_MAP_JSON__", json.dumps(shrine_images, ensure_ascii=False))
    )

    OUTPUT_PATH.write_text(html, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())



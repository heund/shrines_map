import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
OUTPUT_PATH = PROJECT_ROOT / "kakao_test.html"
KAKAO_JS_KEY_ENV = "KAKAO_JAVASCRIPT_KEY"


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


def main() -> int:
    load_env_file(ENV_PATH)
    kakao_js_key = os.environ.get(KAKAO_JS_KEY_ENV, "").strip()
    if not kakao_js_key:
        raise RuntimeError(f"Missing required environment variable: {KAKAO_JS_KEY_ENV}")

    html = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Kakao Maps Test</title>
  <style>
    body {
      margin: 0;
      font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
      background: #f3eee4;
      color: #241d17;
    }
    .wrap {
      min-height: 100vh;
      display: grid;
      grid-template-rows: auto 1fr auto;
    }
    .head, .foot {
      padding: 16px 20px;
      background: #fbf7ef;
      border-bottom: 1px solid rgba(36, 29, 23, 0.08);
    }
    .foot {
      border-bottom: 0;
      border-top: 1px solid rgba(36, 29, 23, 0.08);
      font-size: 0.92rem;
      color: #67584a;
    }
    h1 {
      margin: 0 0 6px;
      font-size: 1.15rem;
    }
    p {
      margin: 0;
      line-height: 1.5;
    }
    #map {
      width: 100%;
      height: calc(100vh - 128px);
      min-height: 520px;
    }
    .status {
      font-weight: 700;
    }
    .ok { color: #116b42; }
    .fail { color: #a53d2d; }
    .debug {
      padding: 16px 20px 20px;
      background: #fffaf2;
      border-top: 1px solid rgba(36, 29, 23, 0.08);
      font-size: 0.92rem;
      line-height: 1.55;
    }
    .debug h2 {
      margin: 0 0 10px;
      font-size: 1rem;
    }
    .debug pre {
      margin: 0;
      padding: 14px;
      white-space: pre-wrap;
      word-break: break-word;
      background: #2a211a;
      color: #f4ebdf;
      border-radius: 12px;
      overflow: auto;
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header class="head">
      <h1>Kakao Maps Minimal Test</h1>
      <p id="status" class="status">SDK loading…</p>
    </header>
    <main id="map"></main>
    <footer class="foot">
      Center: 37.5665, 126.9780 · If this page fails too, the issue is outside the main map interface.
    </footer>
    <section class="debug">
      <h2>Debug</h2>
      <pre id="debugLog">Preparing diagnostics…</pre>
    </section>
  </div>

  <script>
    const debugLines = [];

    function logDebug(message) {
      const line = `[${new Date().toLocaleTimeString("ko-KR", { hour12: false })}] ${message}`;
      debugLines.push(line);
      const el = document.getElementById("debugLog");
      if (el) {
        el.textContent = debugLines.join("\\n");
      }
      console.log(line);
    }

    function setStatus(text, className) {
      const el = document.getElementById("status");
      el.textContent = text;
      el.className = "status " + className;
      logDebug(`STATUS: ${text}`);
    }

    function showMapError(text) {
      setStatus(text, "fail");
      document.getElementById("map").innerHTML =
        `<div style="height:100%;display:grid;place-items:center;padding:24px;text-align:center;font-weight:700;color:#a53d2d;">${text}</div>`;
    }

    function initMap() {
      logDebug(`kakao exists before map init: ${Boolean(window.kakao)}`);
      logDebug(`kakao.maps exists before map init: ${Boolean(window.kakao && window.kakao.maps)}`);
      try {
        const map = new kakao.maps.Map(document.getElementById("map"), {
          center: new kakao.maps.LatLng(37.5665, 126.9780),
          level: 5
        });

        const marker = new kakao.maps.Marker({
          position: new kakao.maps.LatLng(37.5665, 126.9780)
        });
        marker.setMap(map);

        setStatus("Kakao Maps loaded successfully.", "ok");
      } catch (error) {
        logDebug(`Map init exception: ${error.name}: ${error.message}`);
        showMapError("Kakao Maps initialized but map creation failed: " + error.message);
      }
    }

    function loadKakaoSdk() {
      const sdkUrl = "https://dapi.kakao.com/v2/maps/sdk.js?appkey=__KAKAO_JS_KEY__&autoload=false";
      const script = document.createElement("script");
      script.src = sdkUrl;
      script.async = true;
      logDebug(`Page URL: ${location.href}`);
      logDebug(`Page origin: ${location.origin}`);
      logDebug(`User agent: ${navigator.userAgent}`);
      logDebug(`SDK URL: ${sdkUrl}`);
      logDebug(`JS key length: ${"__KAKAO_JS_KEY__".length}`);
      logDebug(`JS key prefix: ${"__KAKAO_JS_KEY__".slice(0, 6)}...`);
      logDebug(`window.kakao before script append: ${Boolean(window.kakao)}`);
      script.onload = () => {
        logDebug("SDK script onload fired.");
        logDebug(`window.kakao after onload: ${Boolean(window.kakao)}`);
        logDebug(`window.kakao.maps after onload: ${Boolean(window.kakao && window.kakao.maps)}`);
        if (!window.kakao || !window.kakao.maps) {
          showMapError("SDK script loaded but kakao.maps is unavailable.");
          return;
        }
        kakao.maps.load(initMap);
      };
      script.onerror = (event) => {
        logDebug(`SDK script onerror fired. Event type: ${event.type}`);
        const perf = performance.getEntriesByName(sdkUrl);
        if (perf && perf.length) {
          const entry = perf[perf.length - 1];
          logDebug(`Performance entry found. transferSize=${entry.transferSize || 0}, duration=${entry.duration.toFixed(2)}ms`);
        } else {
          logDebug("No performance entry found for SDK request.");
        }
        showMapError("Kakao Maps SDK request failed.");
      };
      document.head.appendChild(script);
      logDebug("SDK script appended to document head.");
    }

    window.addEventListener("error", (event) => {
      logDebug(`Window error: ${event.message}`);
    });

    window.addEventListener("unhandledrejection", (event) => {
      logDebug(`Unhandled rejection: ${event.reason}`);
    });

    loadKakaoSdk();
  </script>
</body>
</html>
"""

    OUTPUT_PATH.write_text(html.replace("__KAKAO_JS_KEY__", kakao_js_key), encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

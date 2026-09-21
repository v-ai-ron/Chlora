#!/bin/sh
# Schermo del Pi in kiosk, dopo che il controller risponde.
url=http://127.0.0.1:8080/
python3 - <<'PY'
import time
import urllib.request

url = "http://127.0.0.1:8080/"
for _ in range(30):
    try:
        urllib.request.urlopen(url, timeout=1)
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("Il pannello non risponde su " + url)
PY

if command -v chromium >/dev/null 2>&1; then
  bin=chromium
elif command -v chromium-browser >/dev/null 2>&1; then
  bin=chromium-browser
else
  echo "Chromium non installato" >&2
  exit 1
fi

exec "$bin" \
  --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --start-fullscreen \
  "$url"

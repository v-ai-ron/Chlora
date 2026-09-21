"""Pannello locale. Il Chromium del Pi apre solo questa origine."""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from chlora import config

log = logging.getLogger(__name__)

DISPLAY_DIR = Path(__file__).resolve().parents[2] / "display"
_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


class PanelServer(ThreadingHTTPServer):
    def __init__(self, reactor, host: str, port: int) -> None:
        self.reactor = reactor
        super().__init__((host, port), PanelHandler)


class PanelHandler(BaseHTTPRequestHandler):
    server: PanelServer

    def log_message(self, fmt: str, *args) -> None:
        return

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/state":
            self._send_json(self.server.reactor.snapshot())
            return
        item = _FILES.get(path)
        if item is None:
            self.send_error(404)
            return
        name, content_type = item
        body = (DISPLAY_DIR / name).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path.split("?", 1)[0] != "/api/pump":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw.decode() or "{}")
            mode = body["mode"]
            snap = self.server.reactor.set_pump_mode(mode)
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            self._send_json({"error": "mode deve essere auto, on oppure off"}, status=400)
            return
        self._send_json(snap)

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def serve(reactor) -> None:
    index = DISPLAY_DIR / "index.html"
    if not index.is_file():
        raise SystemExit(f"Schermata non trovata in {index}")
    httpd = PanelServer(reactor, config.HOST, config.PORT)
    log.info("Pannello su http://%s:%s", config.HOST, config.PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

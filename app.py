"""Loopback-only local demo server; all assets are served from this project."""
from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"


def make_handler(engine):
    class Handler(BaseHTTPRequestHandler):
        def reply(self, status, content, mime="application/json; charset=utf-8"):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(content)

        def json_reply(self, status, value):
            self.reply(status, json.dumps(value, allow_nan=False).encode())

        def do_GET(self):
            path = urlparse(self.path).path
            if path == "/api/bootstrap":
                return self.json_reply(200, engine.bootstrap())
            if path == "/api/health":
                return self.json_reply(200, {"ok": True, "simulation": True})
            routes = {"/": "index.html", "/index.html": "index.html", "/style.css": "style.css",
                      "/app.js": "app.js", "/favicon.svg": "favicon.svg"}
            if path not in routes:
                return self.json_reply(404, {"error": "Not found"})
            asset = STATIC / routes[path]
            self.reply(200, asset.read_bytes(), mimetypes.guess_type(asset.name)[0] or "application/octet-stream")

        def do_POST(self):
            if urlparse(self.path).path != "/api/run":
                return self.json_reply(404, {"error": "Not found"})
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 1024:
                    return self.json_reply(400, {"error": "Expected a small JSON request"})
                request = json.loads(self.rfile.read(size))
                if not isinstance(request, dict) or request.get("scenario") not in engine.scenarios:
                    return self.json_reply(400, {"error": "Unknown scenario"})
            except (ValueError, TypeError):
                return self.json_reply(400, {"error": "Invalid JSON request"})
            self.json_reply(200, engine.run(request["scenario"]))

        def log_message(self, fmt, *args):
            print(f"[BLACKSITE] {fmt % args}", flush=True)

    return Handler


def main():
    parser = argparse.ArgumentParser(description="BLACKSITE — local synthetic simulation")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    try:
        from engine import Engine
        engine = Engine()
    except ImportError as error:
        raise SystemExit(f"Missing dependency: {error}. Install requirements.txt in your virtual environment.")
    except FileNotFoundError as error:
        raise SystemExit(f"Missing project data: {error.filename}. Run python generate_data.py.")
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(engine))
    except OSError as error:
        raise SystemExit(f"Cannot start on port {args.port}: {error}. Try --port 8502.")
    print(f"BLACKSITE ready at http://127.0.0.1:{server.server_port}\nSIMULATION — SYNTHETIC DATA ONLY\nCtrl+C to stop.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nSimulation server stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

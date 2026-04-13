import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "worker"}).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps(
                {
                    "service": "worker",
                    "profile": os.environ.get("APP_PROFILE", "development"),
                    "message": "worker runtime active",
                }
            ).encode("utf-8")
        )


def main():
    server = HTTPServer(("0.0.0.0", 8100), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()

import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Arcada is live\n")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()

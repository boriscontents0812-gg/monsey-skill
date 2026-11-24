"""Tiny local helper for the Rizz card: GET serves files from DIR, POST /<name>.png saves the body into DIR.
python card_server.py <DIR>   (listens on 127.0.0.1:8766, CORS open so rizz-template can fetch/POST)"""
import http.server
import os
import re
import sys

DIR = os.path.abspath(sys.argv[1])
os.makedirs(DIR, exist_ok=True)


class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DIR, **k)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
        name = os.path.basename(self.path.split("?")[0])
        if not re.fullmatch(r"[\w.-]+\.(png|jpg|jpeg|json|txt)", name):
            self.send_response(400)
            self.end_headers()
            return
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        with open(os.path.join(DIR, name), "wb") as f:
            f.write(data)
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(str(len(data)).encode())


http.server.ThreadingHTTPServer(("127.0.0.1", 8766), H).serve_forever()

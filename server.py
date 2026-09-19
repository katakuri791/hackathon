#!/usr/bin/env python3
import http.server
import os
import socketserver

PORT = int(os.environ.get("PORT", "8094"))

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as server:
    print(f"Med Assurance starter: http://127.0.0.1:{PORT}")
    server.serve_forever()

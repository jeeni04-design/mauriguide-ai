"""
Simple reverse proxy — routes Render's single $PORT to
Django (:8000) and FastAPI (:8001) based on URL path.

/api/chat/*  → FastAPI :8001
everything else → Django :8000
"""

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError
import urllib.parse

PORT      = int(os.environ.get('PORT', 10000))
DJANGO    = 'http://127.0.0.1:8000'
FASTAPI   = 'http://127.0.0.1:8001'

HOP_HEADERS = {
    'connection','keep-alive','proxy-authenticate','proxy-authorization',
    'te','trailers','transfer-encoding','upgrade'
}

class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence access log noise

    def _target(self):
        path = self.path
        # FastAPI handles: /api/chat/ and /docs and /openapi.json
        if path.startswith('/api/chat') or path.startswith('/docs') or path.startswith('/openapi'):
            return FASTAPI
        return DJANGO

    def _proxy(self, body=None):
        target = self._target() + self.path
        headers = {
            k: v for k, v in self.headers.items()
            if k.lower() not in HOP_HEADERS
        }
        headers['X-Forwarded-For'] = self.client_address[0]
        headers['X-Forwarded-Proto'] = 'https'

        try:
            req = Request(target, data=body, headers=headers, method=self.command)
            with urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in HOP_HEADERS:
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except URLError as e:
            self.send_error(502, f'Bad Gateway: {e}')

    def do_GET(self):    self._proxy()
    def do_POST(self):   self._proxy(self._body())
    def do_PUT(self):    self._proxy(self._body())
    def do_PATCH(self):  self._proxy(self._body())
    def do_DELETE(self): self._proxy()
    def do_OPTIONS(self):self._proxy()

    def _body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length) if length else None

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f'Proxy listening on port {PORT}')
    print(f'  /api/chat/* → FastAPI {FASTAPI}')
    print(f'  everything  → Django  {DJANGO}')
    server.serve_forever()
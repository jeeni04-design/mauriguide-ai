"""
Reverse proxy for MauriGuide AI on Render.
Routes /api/chat/* and /docs to FastAPI :8001
Everything else goes to Django :8000
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.error import URLError

PORT    = int(os.environ.get('PORT', 10000))
DJANGO  = 'http://127.0.0.1:8000'
FASTAPI = 'http://127.0.0.1:8001'

# Headers that must not be forwarded
HOP_HEADERS = {
    'connection', 'keep-alive', 'proxy-authenticate',
    'proxy-authorization', 'te', 'trailers',
    'transfer-encoding', 'upgrade'
}

class ProxyHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def _target(self):
        path = self.path.split('?')[0]
        if (path.startswith('/api/chat') or
            path.startswith('/docs') or
            path.startswith('/openapi') or
            path.startswith('/redoc')):
            return FASTAPI
        return DJANGO

    def _proxy(self, body=None):
        target_url = self._target() + self.path

        # Forward all headers except hop-by-hop
        headers = {}
        for k, v in self.headers.items():
            if k.lower() not in HOP_HEADERS:
                headers[k] = v

        # Add forwarding headers so Django knows it's behind a proxy
        headers['X-Forwarded-For']   = self.client_address[0]
        headers['X-Forwarded-Proto'] = 'https'
        headers['X-Forwarded-Host']  = self.headers.get('Host', '')

        # Critical: tell Django the real host for CSRF and session cookies
        headers['Host'] = '127.0.0.1:8000' if self._target() == DJANGO else '127.0.0.1:8001'

        try:
            req = Request(
                target_url,
                data=body,
                headers=headers,
                method=self.command
            )
            with urlopen(req, timeout=120) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in HOP_HEADERS:
                        # Fix cookie domain so browser stores it correctly
                        if k.lower() == 'set-cookie':
                            v = v.replace('Domain=127.0.0.1', '')
                            v = v.replace('Secure;', '')
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except URLError as e:
            self.send_error(502, f'Bad Gateway: {e.reason}')
        except Exception as e:
            self.send_error(500, f'Internal error: {str(e)}')

    def do_GET(self):     self._proxy()
    def do_POST(self):    self._proxy(self._body())
    def do_PUT(self):     self._proxy(self._body())
    def do_PATCH(self):   self._proxy(self._body())
    def do_DELETE(self):  self._proxy()
    def do_OPTIONS(self): self._proxy()
    def do_HEAD(self):    self._proxy()

    def _body(self):
        length = int(self.headers.get('Content-Length', 0))
        return self.rfile.read(length) if length else None

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', PORT), ProxyHandler)
    print(f'=== Proxy on :{PORT} ===')
    print(f'  /api/chat/* /docs → FastAPI {FASTAPI}')
    print(f'  everything else   → Django  {DJANGO}')
    server.serve_forever()
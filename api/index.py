"""Vercel handler sharing the local application's implementation."""
from urllib.parse import urlparse, parse_qs
from app import make_handler
from engine import Engine

class handler(make_handler(Engine())):
    def restore_route(self):
        route = parse_qs(urlparse(self.path).query).get('route', [None])[0]
        if route is not None:
            self.path = route

    def do_GET(self):
        self.restore_route()
        super().do_GET()

    def do_POST(self):
        self.restore_route()
        super().do_POST()

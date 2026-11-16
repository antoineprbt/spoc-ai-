"""Vercel serverless entry point; same engine and routes as the local app."""
from app import make_handler
from engine import Engine
handler = make_handler(Engine())

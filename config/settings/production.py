from .base import (
    REST_FRAMEWORK,
)

DEBUG = False

ALLOWED_HOSTS = [
    "api.example.com",
    "admin.example.com",
    "localhost",
    "127.0.0.1",
    "server_ip_address",
]

CSRF_TRUSTED_ORIGINS = ["https://api.example.com", "https://admin.example.com"]
CORS_ALLOWED_ORIGINS = ["https://api.example.com", "https://admin.example.com"]
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = False
CORS_ORIGIN_ALLOW_ALL = False

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 7 * 52
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

REST_FRAMEWORK.update(
    {"DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",)}
)

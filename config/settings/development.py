from .base import (
    BASE_APPS,
    THIRD_PARTY_APPS,
    LOCAL_APPS,
    MIDDLEWARE,
)

# Development specific settings
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Debug Toolbar qo'shish
INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + LOCAL_APPS + ["debug_toolbar"]

# Debug Toolbar middleware qo'shish
MIDDLEWARE = MIDDLEWARE + ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# Debug Toolbar settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

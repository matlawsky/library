import os
os.environ.setdefault("DJANGO_SECRET_KEY", "local-development-only-change-for-production")
os.environ.setdefault("DATABASE_URL", "sqlite:///db.sqlite3")
from .settings import *

DEBUG = True
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
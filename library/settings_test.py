import os
os.environ.setdefault("DJANGO_SECRET_KEY", "test-only-not-for-deployment")
os.environ.setdefault("EMAIL_HOST_USER", "test@example.invalid")
os.environ.setdefault("EMAIL_HOST_PASSWORD", "unused")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
MIDDLEWARE = [m for m in MIDDLEWARE if "debug_toolbar" not in m]
STORAGES = {"default": {"BACKEND": "django.core.files.storage.FileSystemStorage"}, "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}}
ACCOUNT_RATE_LIMITS = {}
ACCOUNT_EMAIL_VERIFICATION = "optional"
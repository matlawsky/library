from django.core.exceptions import ImproperlyConfigured
from .settings import *

if len(SECRET_KEY) < 50 or SECRET_KEY.startswith(("local-", "test-")):
    raise ImproperlyConfigured("A strong production DJANGO_SECRET_KEY is required.")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS")

if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Explicit production hosts are required.")

CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env.str("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT",587)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

# Enable only behind a trusted proxy which strips incoming forwarded headers.
if env.bool("TRUST_PROXY_SSL_HEADER",False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO","https")
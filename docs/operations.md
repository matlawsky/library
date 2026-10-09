# Operation
Local: copy .env.example to .env, choose a password, then `docker compose up -d db`.
Run `docker compose run --rm web python manage.py migrate` once, then `docker compose up -d web`.
Static assets are built into the image. Run `createsuperuser` interactively; do not commit passwords.
Production: set DJANGO_SETTINGS_MODULE=library.settings_prod, SMTP, allowed hosts, CSRF origins and a strong secret. Use a TLS-terminating trusted proxy. Application migration is a separate release step, never per Gunicorn worker.
Use /health/live/ for process health and /health/ready/ for DB readiness. Configure the proxy to check them with the expected HTTPS scheme. Do not expose DB ports publicly.
See database-upgrade.md before changing the PostgreSQL major version.
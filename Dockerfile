FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock && useradd --create-home --uid 10001 app
COPY --chown=app:app . .
RUN DJANGO_SETTINGS_MODULE=library.settings_dev python manage.py collectstatic --noinput && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["gunicorn", "library.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--access-logfile", "-"]
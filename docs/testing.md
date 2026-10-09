# Tests
Run `python manage.py test --settings=library.settings_test`.
Set DATABASE_URL to a disposable PostgreSQL database for transaction tests.
Never point test settings at production. SMTP uses an in-memory backend.
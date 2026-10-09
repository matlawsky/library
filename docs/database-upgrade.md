# PostgreSQL 13 -> 16
Do not reuse the PostgreSQL 13 data directory with version 16.
1. Stop application writes. Back up using `pg_dump -Fc` with a compatible client.
2. Keep the old volume and start PostgreSQL 16 on a NEW volume.
3. Restore with `pg_restore --no-owner --exit-on-error` into an empty database.
4. Compare Book, Copy and Event counts and run audit_circulation --dry-run.
5. Run migrations, tests and a reserve/issue/return scenario; only then switch DATABASE_URL.
6. Keep the source volume until recovery has been tested. Application rollback after new writes needs a data reconciliation plan.
# Database Migrations

## Overview

This directory contains versioned SQL migrations for the LinguaBot database schema.

## Migration Naming Convention

```
<version>_<description>.sql
```

- `<version>`: 3-digit number (001, 002, etc.)
- `<description>`: Snake_case description of the migration

## Migration Format

```sql
-- Migration <version>: <Title>
-- Date: YYYY-MM-DD
-- Task: <Related task from IMPLEMENTATION_PLAN.md>

<SQL statements>
```

## How Migrations Work

1. **Tracking**: The `schema_migrations` table tracks which migrations have been applied
2. **Auto-apply**: Migrations run automatically on bot startup via `Database.apply_migrations()`
3. **Idempotent**: Use `IF NOT EXISTS` / `IF EXISTS` to make migrations safe to re-run
4. **Order**: Migrations execute in alphabetical/numerical order
5. **Atomic**: Each migration runs in a transaction - either ALL statements succeed or ALL rollback
6. **Fail-fast**: If a migration fails, the bot stops startup and reports the error

## Creating a New Migration

1. Create file: `migrations/XXX_description.sql` (increment version number)
2. Write SQL using PostgreSQL and SQLite compatible syntax when possible
3. Test locally: `docker compose -f docker-compose.dev.yml restart linguabot`
4. Verify: Check `schema_migrations` table for the new version

## Manual Migration

If needed, apply manually:

```bash
# PostgreSQL (Docker)
docker exec linguabot_postgres_dev psql -U linguabot -d linguabot -f /path/to/migration.sql

# PostgreSQL (Railway)
psql $DATABASE_URL -f migrations/XXX_description.sql
```

## Existing Migrations

- **001_add_is_blocked.sql**: User blocking feature (Task 2.1)
- **002_add_performance_metrics.sql**: Performance tracking (Task 2.4)

## Notes

- ⚠️ Never delete or modify existing migration files
- ⚠️ Never change version numbers of applied migrations
- ✅ Always use `ADD COLUMN IF NOT EXISTS` for safety
- ✅ Always test migrations on dev environment first

## Troubleshooting

### Migration Failed with "duplicate key" Error

**Problem**: Migration marked as applied in `schema_migrations`, but schema changes didn't apply.

**Symptoms**:
```
[MIGRATIONS] ❌ Failed to apply: duplicate key value violates unique constraint "schema_migrations_pkey"
asyncpg.exceptions.UndefinedColumnError: column does not exist
```

**Solution**:
1. Create fix script to manually apply the migration
2. Delete the failed entry from `schema_migrations`
3. Re-run the migration

**Example fix script**:
```sql
-- Delete failed migration record
DELETE FROM schema_migrations WHERE version = 'XXX_migration_name.sql';

-- Manually apply the migration
ALTER TABLE users ADD COLUMN IF NOT EXISTS new_column TEXT;

-- Re-insert migration record
INSERT INTO schema_migrations (version) VALUES ('XXX_migration_name.sql');
```

### Best Practices for Future Migrations

1. **Always use IF NOT EXISTS / IF EXISTS**
   - Makes migrations idempotent
   - Safe to re-run multiple times

2. **Test locally first**
   ```bash
   # Test on local Docker
   docker compose -f docker-compose.dev.yml restart linguabot
   # Check logs for [MIGRATIONS] messages
   ```

3. **One logical change per migration**
   - Don't mix unrelated schema changes
   - Easier to rollback if needed

4. **Document breaking changes**
   - Add comment in migration file explaining impact
   - Update CLAUDE.md if affects development workflow

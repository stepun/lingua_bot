# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LinguaBot is an AI-powered Telegram translator bot with freemium model. It features multi-tier translation (DeepL/Yandex → GPT-4o enhancement), voice processing, payment integration, and comprehensive user management.

## Core Architecture

### Translation Pipeline
The bot uses a sophisticated 2-stage translation system:
1. **Primary Translation**: DeepL API → Yandex Translate → Google Translate (fallback chain)
2. **AI Enhancement**: OpenAI GPT-4o post-processing for style, context, and quality improvement

Translation service priority is defined in `bot/services/translator.py:236-246`:
- DeepL (highest quality, requires API key)
- Yandex (good Russian support, requires API key)
- Google Translate (fallback, no key needed)

### Entry Point
- `main.py` - Full aiogram-based bot with all features

### Configuration System
All configuration is centralized in `config.py` with environment variable loading. Key models:
- GPT_MODEL = "gpt-4o" (configurable)
- WHISPER_MODEL = "whisper-1"
- Database path, pricing, limits all configurable

### Database Architecture
PostgreSQL-based with async operations in `bot/database.py`:
- User management with subscription tracking
- Daily usage limits and premium features
- Translation history storage
- Payment tracking

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run bot in development mode
python3 .scripts/run_dev.py      # Development mode with PostgreSQL
python3 .scripts/run_admin.py    # Admin panel only
python main.py                   # Production mode

# Database utilities
python3 .scripts/init_db.py      # Initialize database
python3 .scripts/migrate_data.py # Migrate data between databases
python3 run_migrations.py        # Run migrations
```

### Docker Development
```bash
# Build and run with Docker
docker-compose up --build -d

# Development with PostgreSQL
docker-compose -f docker-compose.dev.yml up -d

# Use management scripts (in .scripts/)
.scripts/docker-start.sh       # Interactive menu for Docker management (Linux/macOS)
.scripts/docker-start.bat      # Windows version
.scripts/start_bot.sh          # Start bot locally
.scripts/stop_bot.sh           # Stop bot locally
.scripts/start_monitor.sh      # Start with monitoring
.scripts/status.sh             # Check bot status

# View logs
docker-compose logs -f linguabot

# Stop
docker-compose down
```

### Testing Translation Chain
The bot automatically falls back through translation services. To test:
1. Configure API keys in `.env`
2. Send text to bot
3. Check logs for service usage order

## Environment Configuration

Required variables in `.env`:
- `BOT_TOKEN` - Telegram Bot token from BotFather
- `OPENAI_API_KEY` - OpenAI API key for GPT-4o

Optional but recommended:
- `DEEPL_API_KEY` - For best translation quality
- `YANDEX_API_KEY` - For good Russian language support
- `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY` - For YooKassa payments
- `PROVIDER_TOKEN` - For Telegram native payments
- `ELEVENLABS_API_KEY` - For premium voice synthesis

## Key Service Interactions

### Translation Flow
1. Text received → `bot/handlers/base.py`
2. User limits checked → `bot/database.py`
3. Translation service called → `bot/services/translator.py`
4. GPT enhancement applied → OpenAI API
5. Result returned with usage tracking

### Voice Processing
- Input: Whisper API for speech-to-text
- Output: OpenAI TTS or ElevenLabs for premium users
- Handled in `bot/services/voice.py`

### Payment System
- YooKassa and Telegram native payments in `bot/services/payment.py`
- Webhook handling in `bot/handlers/payments.py` and `webhook.py` (YooKassa callbacks)
- Subscription management in database layer
- Receipt generation for fiscal compliance (provider_data)
- ⚠️ **Critical**: `webhook.py` is required for YooKassa payment processing in production

## Docker Architecture

Multi-stage Dockerfile optimized for production:
- Python 3.11 slim base
- Non-root user (linguabot)
- Health checks via PostgreSQL connection test
- Resource limits: 512MB RAM, 0.5 CPU
- Volume mounts for persistent data: `./data`, `./logs`, `./exports`

The Docker setup runs `main.py` with all features enabled.

## File Structure Notes

- `bot/handlers/` - Message processing and user interactions
- `bot/services/` - Business logic (translation, voice, payments, export)
- `bot/keyboards/` - Telegram UI components
- `bot/middlewares/` - Request processing middleware
- `bot/utils/` - Shared utilities and messages
- `data/` - PostgreSQL database backups and user data
- `logs/` - Application logs
- `exports/` - Generated PDF/TXT exports
- `.scripts/` - Local development scripts (not tracked in git)

### Development Scripts Organization

All local development scripts are located in `.scripts/` directory (excluded from git):

**Bot Management:**
- `run_dev.py` - Run bot with PostgreSQL in development mode
- `run_admin.py` - Run admin panel standalone
- `start_bot.sh` / `start_bot.bat` - Start bot locally
- `stop_bot.sh` - Stop local bot instance
- `bot_monitor.py` - Process monitoring with auto-restart
- `start_monitor.sh` - Start bot with monitoring
- `check_and_restart.sh` - Health check and restart script
- `status.sh` - Check bot status

**Docker Management:**
- `docker-start.sh` - Interactive Docker management menu (Linux/macOS)
- `docker-start.bat` - Interactive Docker management menu (Windows)
- `dev.sh` - Development environment setup

**Database Utilities:**
- `init_db.py` - Initialize database schema
- `migrate_data.py` - Migrate data between databases
- `delete_webhook.py` - Delete Telegram webhook

**Production Scripts (in root):**
- `main.py` - Main bot entry point
- `config.py` - Configuration management
- `webhook.py` - YooKassa payment webhook handler ⚠️ **Required for production**
- `install_beget.sh` - Install bot on Beget server
- `start_beget.sh` - Start bot on Beget
- `stop_beget.sh` - Stop bot on Beget
- `run_migrations.py` - Apply database migrations
- `apply_migrations_public.py` - Apply migrations to Railway

## Remote Server Access

SSH credentials and deployment info are in `creds.md`:
- Server: `ssh vokhma1v@vokhma1v.beget.tech`
- Project path: `/home/v/vokhma1v/vokhma1v.beget.tech/lingua_bot`

### Server Management Scripts
```bash
# Server deployment and management (production)
./install_beget.sh            # Install bot on Beget server
./start_beget.sh              # Start bot on Beget server
./stop_beget.sh               # Stop bot on server

# Local development scripts (in .scripts/)
.scripts/run_dev.py           # Run bot in development mode
.scripts/run_admin.py         # Run admin panel only
.scripts/start_bot.sh         # Start bot locally
.scripts/stop_bot.sh          # Stop bot locally
.scripts/start_monitor.sh     # Start with monitoring
.scripts/check_and_restart.sh # Restart if crashed
.scripts/status.sh            # Check bot status
.scripts/bot_monitor.py       # Process monitoring with auto-restart
```

## Database Schema

### Enhanced Translation History
The `translation_history` table stores comprehensive translation data:
- `basic_translation` - Direct translation result
- `enhanced_translation` - GPT-4o enhanced version
- `alternatives` - JSON array of alternative translations
- Enables proper voice synthesis for exact/styled/alternative translations

### Voice Handler Architecture
Voice handlers have strict data isolation:
- **Voice Exact** → uses `basic_translation` from metadata/history
- **Voice Styled** → uses `enhanced_translation` from metadata/history
- **Voice Alternatives** → uses parsed JSON `alternatives` from metadata/history
- Fallback logic queries database when `last_translation_metadata` is empty

## Translation Metadata Flow

1. **Memory Storage**: `last_translation_metadata` dict stores current session data
2. **Database Persistence**: All translations saved with basic/enhanced/alternatives fields
3. **Voice Handlers**: Use memory first, fallback to database for reliability
4. **Data Isolation**: Each voice type has dedicated data source to prevent mixing

## Monitoring System

- `.scripts/bot_monitor.py` - Process monitoring with auto-restart
- PID tracking in `/tmp/bot.pid` and `/tmp/monitor.pid`
- Automatic health checks and recovery
- Detailed logging in `logs/bot.log` and `logs/monitor.log`

## Middleware Architecture

- `bot/middlewares/throttling.py` - Rate limiting (configurable in config)
- `bot/middlewares/user_middleware.py` - Automatic user registration
- `bot/middlewares/admin.py` - Admin access control

## Common Issues

1. **ADMIN_IDS format**: Must be numeric Telegram user ID, not username/URL
2. **Docker not starting**: Ensure Docker Desktop is installed and WSL integration enabled
3. **Translation failures**: Check API keys and account balances, services fail gracefully
4. **Voice TTS errors**:
   - Invalid voice_type (must be: alloy, echo, fable, onyx, nova, shimmer, ash, sage, coral)
   - Check OpenAI API key and ElevenLabs configuration
   - Ensure Telegram voice message permissions are enabled
5. **YooKassa payment errors**: Ensure `need_email=true` and `provider_data` are set for receipt generation
6. **Admin panel database connection errors in Docker**:
   - **Symptom**: Admin panel shows "Loading..." forever, API endpoints return 500 errors with `socket.gaierror: [Errno -2] Name or service not known`
   - **Cause**: Postgres container in different Docker network (e.g., "bridge" instead of "linguabot_dev_network")
   - **Fix**: Fully recreate all containers:
     ```bash
     docker stop linguabot_postgres_dev && docker rm linguabot_postgres_dev
     docker compose -f docker-compose.dev.yml down
     docker compose -f docker-compose.dev.yml up -d
     ```
   - **Why it happens**: When using `docker compose up -d --force-recreate --no-deps linguabot`, only the bot container is recreated, leaving postgres in the old network
   - **How to verify fix**: Check both containers are in the same network:
     ```bash
     docker network inspect linguabot_dev_network --format '{{range $key, $value := .Containers}}{{$value.Name}}{{"\n"}}{{end}}'
     # Should show both: linguabot_postgres_dev and linguabot_dev
     ```
7. **"No module named 'webhook'" error on Railway**:
   - **Symptom**: Bot crashes with `ModuleNotFoundError: No module named 'webhook'`
   - **Cause**: `webhook.py` file was accidentally deleted during cleanup
   - **Fix**: Restore `webhook.py` from git history or backup - it's required for YooKassa payment processing
   - **Prevention**: Never delete these production-critical files:
     - `webhook.py` - YooKassa payment webhook handler
     - `main.py` - Bot entry point
     - `config.py` - Configuration management
     - Files in `bot/` directory - core bot functionality

## Database Migrations System

The project uses a custom versioned migrations system to prevent schema inconsistencies.

### How It Works

1. **Tracking Table**: `schema_migrations` stores applied migration versions
2. **Migration Files**: Stored in `migrations/` directory with format `XXX_description.sql`
3. **Auto-Apply**: Migrations run automatically on bot startup via `Database.apply_migrations()` (bot/database.py:295)
4. **Idempotent**: All migrations use `ADD COLUMN IF NOT EXISTS` to safely re-run

### Migration Naming Convention

```
XXX_description.sql
```

- `XXX`: 3-digit version number (001, 002, ...)
- `description`: Snake_case description

### Creating a New Migration

1. Create file in `migrations/`:
   ```bash
   touch migrations/003_add_new_feature.sql
   ```

2. Write idempotent SQL:
   ```sql
   -- Migration 003: Add new feature
   -- Date: 2025-10-01
   -- Task: 3.5 - Feature description

   ALTER TABLE users ADD COLUMN IF NOT EXISTS new_field TEXT DEFAULT '';
   ```

3. **Local (Docker)**: Restart bot to apply:
   ```bash
   docker compose -f docker-compose.dev.yml restart linguabot
   ```

4. **Railway (Production)**: Apply manually (see below)

5. Verify:
   ```bash
   # Local Docker
   docker exec linguabot_postgres_dev psql -U linguabot -d linguabot -c "SELECT * FROM schema_migrations;"

   # Railway
   python3 apply_migrations_public.py
   ```

### Applying Migrations on Railway

⚠️ **IMPORTANT**: Automatic migrations are **DISABLED** on Railway due to deployment hangs.

Migrations must be applied manually after deployment:

```bash
# Apply migrations via public Railway URL
python3 apply_migrations_public.py
```

This script:
1. Connects to Railway PostgreSQL via public URL
2. Shows current migration state
3. Applies pending migrations
4. Verifies results

**Why manual?** Automatic migrations cause Railway deployments to hang indefinitely during database initialization. Manual application avoids this issue.

### Existing Migrations

- `001_add_is_blocked.sql`: User blocking feature (Task 2.1)
- `002_add_performance_metrics.sql`: Performance tracking (Task 2.4)
- `003_remove_premium_fields.sql`: Remove redundant premium fields from users table
- `004_reset_migration_003.sql`: Reset migration 003 for re-application
- `005_add_test_field.sql`: Test field for migration system validation (can be removed)

### Important Notes

- ⚠️ **Never delete or modify existing migration files**
- ⚠️ **Never change version numbers of applied migrations**
- ⚠️ **On Railway: migrations MUST be applied manually via `apply_migrations_public.py`**
- ✅ **Always use `IF NOT EXISTS` / `IF EXISTS` for safety**
- ✅ **Always test on dev environment first**
- ✅ **Docker volume `postgres_dev_data` persists data between restarts**

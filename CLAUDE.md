# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LinguaBot is an AI-powered Telegram translator bot with freemium model. It features multi-tier translation (DeepL/Yandex → GPT-4o enhancement), voice processing, payment integration, and comprehensive user management.

### 🟢 Production Status (Updated: 07.10.2025)

**Live Bot:** @PolyglotAI44_bot
**Domain:** https://voice2lang.ru (SSL: ✅ Active until 05.01.2026)
**Server:** Selectel VPS (213.148.11.142) - SSH: `ssh FARUH`
**Mode:** Webhook (HTTPS)
**Database:** PostgreSQL 16 (local, migrated from Railway)
**Status:** ✅ **OPERATIONAL**

Quick health check:
```bash
ssh FARUH 'systemctl status linguabot'
ssh FARUH 'tail -20 /opt/linguabot/logs/bot.log'
curl -I https://voice2lang.ru/admin
```

## Core Architecture

### Translation Pipeline
The bot uses a sophisticated 2-stage translation system:
1. **Primary Translation**: DeepL API → Yandex Translate → Google Translate (fallback chain)
2. **AI Enhancement**: OpenAI GPT-4o post-processing for style, context, and quality improvement
3. **IPA Transcription** (Premium): GPT-4o generates phonetic transcription for basic translation

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
- `admin_app/` - Admin panel WebApp (aiohttp + Telegram WebApp integration)
  - `static/modules/users_v2.js` - User management module (renamed to bypass Telegram WebApp cache)
  - `app.py` - Route setup with no-cache headers for static files
  - `handlers/users.py` - Includes `premium_until` field in user data
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

### Production Server (voice2lang.ru)
- **SSH**: `ssh FARUH`
- **Server IP**: 213.148.11.142
- **Domain**: voice2lang.ru ✅ **CONFIGURED** (SSL active until 05.01.2026)
- **Bot**: @PolyglotAI44_bot (token: 7833039830:AAFtpgWKphLaFxGnxExkWn6aG6Mm2EQC6wg)
- **Project path**: `/opt/linguabot`
- **User**: root
- **OS**: Ubuntu 24.04 LTS
- **Status**: 🟢 **PRODUCTION** (deployed 07.10.2025)

### Old Beget Server (deprecated)
- Server: `ssh vokhma1v@vokhma1v.beget.tech`
- Project path: `/home/v/vokhma1v/vokhma1v.beget.tech/lingua_bot`

### Production Server Management (voice2lang.ru)

**System Service:**
```bash
# Service control
ssh FARUH 'systemctl start linguabot'   # Start bot
ssh FARUH 'systemctl stop linguabot'    # Stop bot
ssh FARUH 'systemctl restart linguabot' # Restart bot
ssh FARUH 'systemctl status linguabot'  # Check status

# Logs
ssh FARUH 'tail -f /opt/linguabot/logs/bot.log'        # Main logs
ssh FARUH 'tail -f /opt/linguabot/logs/bot_error.log'  # Error logs
ssh FARUH 'journalctl -u linguabot -f'                 # System logs

# Configuration
ssh FARUH 'nano /opt/linguabot/.env'                   # Edit environment
ssh FARUH 'systemctl daemon-reload'                    # Reload systemd after changes
```

**Deployment:**
- Service file: `/etc/systemd/system/linguabot.service`
- Auto-starts on boot
- Automatic restart on failure (RestartSec=10)
- Logs to `/opt/linguabot/logs/`

**Environment:**
- Python 3.12.3
- PostgreSQL 16 (local), upgraded to PostgreSQL 17 client tools
- Nginx 1.24.0 (reverse proxy with SSL)
- No Docker (native installation)

**Current Mode:**
- ✅ **Webhook mode ACTIVE**: PORT=8080
- ✅ **SSL/HTTPS enabled**: Let's Encrypt certificate
- ✅ **Database**: Migrated from Railway (7 users, 65 translations)
- ✅ **PROVIDER_TOKEN**: Configured for Telegram Payments (390540012:LIVE:78592)

### DNS and SSL Setup ✅ COMPLETED

**✅ DNS Configured:**
```bash
voice2lang.ru → 213.148.11.142 (A record)
# Note: www.voice2lang.ru subdomain not configured (DNS NXDOMAIN)
```

**✅ SSL Certificate Installed:**
```bash
# Installed: certbot 2.9.0 + python3-certbot-nginx
# Certificate: /etc/letsencrypt/live/voice2lang.ru/
# Expiry: 2026-01-05 (auto-renewal enabled via systemd timer)
# Command used:
ssh FARUH 'certbot certonly --webroot -w /var/www/html -d voice2lang.ru --non-interactive --agree-tos -m admin@voice2lang.ru'
```

**✅ Webhook Mode Active:**
```bash
# .env configuration:
PORT=8080
WEBHOOK_HOST=https://voice2lang.ru
BOT_TOKEN=7833039830:AAFtpgWKphLaFxGnxExkWn6aG6Mm2EQC6wg
PROVIDER_TOKEN=390540012:LIVE:78592
```

**✅ Nginx Configuration:**
- Config: `/etc/nginx/sites-available/linguabot`
- HTTP (port 80) → HTTPS redirect
- HTTPS (port 443) → proxy to localhost:8080
- Handles both webhook and admin panel
- SSL auto-renewal via certbot systemd timer
- SSL protocols: TLSv1.2, TLSv1.3

### Old Beget Server Scripts (deprecated)
```bash
./install_beget.sh            # Install bot on Beget server
./start_beget.sh              # Start bot on Beget server
./stop_beget.sh               # Stop bot on server
```

### Database Migration (Railway → Production Server)

**✅ Completed: 07.10.2025**

Migration from Railway PostgreSQL 17 to local PostgreSQL 16 on voice2lang.ru server:

```bash
# 1. Backup current database on FARUH
ssh FARUH 'PGPASSWORD=linguabot_pass_2025 pg_dump -h localhost -U linguabot -d linguabot > /opt/linguabot/backups/linguabot_backup_$(date +%Y%m%d_%H%M%S).sql'

# 2. Install PostgreSQL 17 client tools for compatibility
ssh FARUH 'wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -'
ssh FARUH 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
ssh FARUH 'apt update && apt install -y postgresql-client-17'

# 3. Download Railway database dump
ssh FARUH 'PGPASSWORD=NtLFItrylcyGPGHIqllCxepVRNTSkHYG /usr/lib/postgresql/17/bin/pg_dump -h hopper.proxy.rlwy.net -p 52905 -U postgres -d railway --no-owner --no-acl -f /opt/linguabot/backups/railway_dump.sql'

# 4. Recreate database
ssh FARUH 'sudo -u postgres psql -c "DROP DATABASE IF EXISTS linguabot;"'
ssh FARUH 'sudo -u postgres psql -c "CREATE DATABASE linguabot OWNER linguabot;"'

# 5. Restore Railway dump
ssh FARUH 'PGPASSWORD=linguabot_pass_2025 psql -h localhost -U linguabot -d linguabot -f /opt/linguabot/backups/railway_dump.sql'

# 6. Restart bot
ssh FARUH 'systemctl restart linguabot'
```

**Migrated Data:**
- Users: 7
- Translation history: 65 records
- Admin roles: 2
- System settings: 21
- Tables: admin_actions, admin_roles, feedback, schema_migrations, statistics, subscriptions, system_settings, translation_history, user_settings, users

**Database Credentials:**
- Host: localhost:5432
- User: linguabot
- Database: linguabot
- Password: linguabot_pass_2025

**Backup Location:** `/opt/linguabot/backups/`

### Local Development Scripts
```bash
# Development scripts (in .scripts/)
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
- `transcription` - IPA (International Phonetic Alphabet) transcription for basic translation (premium feature)
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

## Phonetic Transcription (IPA)

**Premium Feature**: Displays International Phonetic Alphabet transcription for translations.

### Configuration
- **User Setting**: `show_transcription` in `user_settings` table (default: FALSE)
- **Database Field**: `transcription` in `translation_history` table
- **Toggle**: Premium users can enable/disable via Settings → 📝 Показывать транскрипцию

### Implementation Details
- **Generation**: GPT-4o generates IPA for **ALL translation variants**: basic, enhanced, and all alternatives
- **Location**: `bot/services/translator.py` - added to GPT prompt with explicit instructions
- **Storage Format**: Alternatives now stored as `{'text': '...', 'transcription': '...'}` dict (not plain strings)
- **Display**: Shows in chat as `🗣️ [IPA notation]` for each translation variant when enabled
- **Export**: Included in both PDF and TXT exports with label "Транскрипция:"

### Critical Prompt Instructions
```
IMPORTANT: Create IPA transcriptions for:
- Basic translation: "{translated_text}"
- Enhanced/styled translation
- Each alternative translation

Format:
Enhanced: [text]
EnhancedTranscription: [IPA]
Alternative1: [text]
Alternative1Transcription: [IPA]
...
```

### Display Format
```
📝 Точный перевод:
Hello

🗣️ [həˈləʊ]

✨ Стилизованный перевод (неформальный):
Hey there!
```

### Files Modified
- `bot/services/translator.py` - GPT prompt and parsing
- `bot/handlers/base.py` - Display logic (lines ~282, ~457) and history saving
- `bot/keyboards/inline.py` - Settings UI button (premium only)
- `bot/handlers/callbacks.py` - Toggle handler
- `bot/database.py` - Field validation, retrieval, storage
- `bot/services/export.py` - PDF/TXT export formatting

### Migrations
- `009_add_show_transcription.sql` - Adds `show_transcription` to `user_settings`
- `010_add_transcription_to_history.sql` - Adds `transcription` to `translation_history`

## Monitoring System

- `.scripts/bot_monitor.py` - Process monitoring with auto-restart
- PID tracking in `/tmp/bot.pid` and `/tmp/monitor.pid`
- Automatic health checks and recovery
- Detailed logging in `logs/bot.log` and `logs/monitor.log`

## Middleware Architecture

- `bot/middlewares/throttling.py` - Rate limiting (configurable in config)
- `bot/middlewares/user_middleware.py` - Automatic user registration
- `bot/middlewares/admin.py` - Admin access control

## Admin Panel

The admin panel is a Telegram WebApp-based interface for managing users, viewing statistics, and monitoring bot activity. Located in `admin_app/` directory.

### Features

**User Management:**
- View all users with pagination and search
- Grant/revoke premium subscriptions (1 day increments)
- Block/unblock users
- Send direct messages to users via bot
- View user translation history

**Statistics Dashboard:**
- Total users, premium users, active today
- Daily translation statistics (7-day chart)
- Language pair statistics
- Performance metrics (avg processing time, success rate)
- Error tracking by day

**Logs & Monitoring:**
- Translation logs (text/voice filtering)
- System logs (last 50 lines)
- Admin action logs (all admin operations tracked)

**Feedback Management:**
- View user feedback
- Filter by status (new/reviewed/resolved)
- Update feedback status

### Admin Action Logging

All admin operations are automatically logged to `admin_actions` table with details:

**Logged Actions:**
- `grant_premium` - Granting premium subscription
- `ban_user` - Blocking user
- `unban_user` - Unblocking user
- `send_message` - Sending message to user (preview + length stored)
- `update_feedback` - Changing feedback status
- `view_history` - Viewing user translation history

**Important:** Admin action logging uses `?` placeholders that are converted to PostgreSQL `$N` syntax by `db_adapter`. Never use `$1, $2...` directly in `database.py` - always use `?`.

### Responsive Design

**Mobile Navigation (≤640px):**
- Icon-only navigation (📊 👥 📝 💬 🔒)
- Hidden text labels to save space
- Touch-optimized tap targets (14px padding)

**Desktop/Tablet (>640px):**
- Icon + text navigation
- Flexbox layout with proper spacing

### Sending Messages to Users

Admins can send messages directly to users through the admin panel:

1. Navigate to Users tab
2. Click "Send Message" button (between "Grant Premium" and "Block")
3. Enter message text in modal dialog
4. Message is sent via bot with format: `📩 Message from admin:\n\n{text}`
5. Action is logged to admin_actions with message preview

**Implementation:**
- API endpoint: `POST /api/users/{user_id}/send-message`
- Creates new Bot instance for sending
- Validates admin permissions via Telegram WebApp authentication
- Logs action with first 100 chars of message

### Access Control & Role-Based Permissions

**Authentication:**
- Telegram WebApp initData with HMAC validation
- Dual-mode: Database-first (admin_roles table) with ADMIN_IDS fallback

**Role System (RBAC):**
- **Admin** - Full access to all features (`*` permission)
- **Moderator** - User management, logs, feedback (view_users, block_user, view_logs, etc.)
- **Analyst** - Read-only statistics (view_dashboard, view_stats only)

**Permission Checking:**
- `check_admin_with_permission(request, 'permission_name')` - Returns (user_id, role, permissions)
- Database role takes precedence over ADMIN_IDS
- All endpoints protected with specific permission requirements
- HTTP 403 for insufficient permissions (re-raised before generic Exception catch)

**Bot Integration:**
- `check_admin_role(user_id)` in bot/middlewares/admin.py
- All admin commands (/admin_panel, /admin, etc.) use async role checking
- Fallback to ADMIN_IDS for backward compatibility

### File Structure

**Core Application:**
- `admin_app/app.py` - Route registration and static file serving
- `admin_app/auth.py` - Telegram WebApp authentication and role permissions
- `admin_app/static/index.html` - Single-page application UI
- `admin_app/static/app.js` - Frontend logic, API calls, i18n translations
- `admin_app/static/style.css` - Legacy styles (most use Tailwind inline)

**Modular Handlers (admin_app/handlers/):**
- `stats.py` - Statistics endpoints (overall, daily, languages, performance)
- `users.py` - User management (list, block/unblock, premium, messages, history)
- `logs.py` - Translation logs
- `feedback.py` - User feedback management
- `admin_logs.py` - Admin action logs
- `roles.py` - Role management (assign, remove, list)

All handlers use `check_admin_with_permission()` for authorization and re-raise HTTPException before catching generic errors.

## Common Issues

1. **ADMIN_IDS format**: Must be numeric Telegram user ID, not username/URL
2. **Docker not starting**: Ensure Docker Desktop is installed and WSL integration enabled
3. **Translation failures**: Check API keys and account balances, services fail gracefully
4. **Production deployment - webhook domain not resolving**:
   - **Symptom**: Bot fails to start with `Bad Request: bad webhook: Failed to resolve host: Name or service not known`
   - **Cause**: DNS not configured or not propagated yet
   - **Fix**: Switch to polling mode temporarily: `ssh FARUH 'cd /opt/linguabot && sed -i "s/^PORT=8080/PORT=0/" .env && systemctl restart linguabot'`
   - **Permanent solution**: Configure DNS A-record pointing to server IP, install SSL certificate, then switch back to webhook mode
5. **Voice TTS errors**:
   - Invalid voice_type (must be: alloy, echo, fable, onyx, nova, shimmer, ash, sage, coral)
   - Check OpenAI API key and ElevenLabs configuration
   - Ensure Telegram voice message permissions are enabled
6. **YooKassa payment errors**: Ensure `need_email=true` and `provider_data` are set for receipt generation
7. **Admin panel database connection errors in Docker**:
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
8. **"No module named 'webhook'" error on Railway**:
   - **Symptom**: Bot crashes with `ModuleNotFoundError: No module named 'webhook'`
   - **Cause**: `webhook.py` file was accidentally deleted during cleanup
   - **Fix**: Restore `webhook.py` from git history or backup - it's required for YooKassa payment processing
   - **Prevention**: Never delete these production-critical files:
     - `webhook.py` - YooKassa payment webhook handler
     - `main.py` - Bot entry point
     - `config.py` - Configuration management
     - Files in `bot/` directory - core bot functionality
9. **PostgreSQL datetime handling - "'datetime.datetime' object is not subscriptable"**:
   - **Symptom**: Errors in export (PDF/TXT), history display: `TypeError: 'datetime.datetime' object is not subscriptable`
   - **Cause**: PostgreSQL returns `created_at` as `datetime.datetime` object, not string. Code using string slicing like `item['created_at'][:19]` fails
   - **Solution**: Always check type before string operations:
     ```python
     from datetime import datetime
     created_at = item['created_at']
     if isinstance(created_at, datetime):
         date_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
     else:
         date_str = created_at[:19]  # Fallback for string format
     ```
   - **Affected files**:
     - `bot/services/export.py` - PDF/TXT generation (lines 150-159, 172-184, 267-277, 291-302)
     - `bot/handlers/export.py` - Export handlers (lines 58-70, 128-140)
     - `bot/handlers/callbacks.py` - History display (lines 311-321)
   - **Prevention**: Always use `isinstance(value, datetime)` when working with database date fields
10. **Backslashes in translation text - escape_markdown issue**:
   - **Symptom**: Translation messages show backslashes before punctuation: `Hello\!How are you\?`
   - **Cause**: Using `escape_markdown()` with Markdown parse mode, which escapes characters like `.`, `!`, `?`, `-`, etc.
   - **Solution**: Switch from Markdown to HTML formatting:
     ```python
     # OLD (incorrect)
     def escape_markdown(text: str) -> str:
         special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
         for char in special_chars:
             text = text.replace(char, '\\' + char)
         return text

     await message.answer(text, parse_mode='Markdown')

     # NEW (correct)
     def escape_html(text: str) -> str:
         text = text.replace('&', '&amp;')
         text = text.replace('<', '&lt;')
         text = text.replace('>', '&gt;')
         return text

     await message.answer(text, parse_mode='HTML')
     ```
   - **Formatting changes**:
     - `*текст*` or `**текст**` → `<b>текст</b>` (bold)
     - `` `код` `` → `<code>код</code>` (code)
     - `_текст_` → `<i>текст</i>` (italic)
   - **Affected files** (fixed 07.10.2025):
     - `bot/handlers/base.py` - Main translation and voice handlers
     - `bot/handlers/callbacks.py` - All callback handlers (alternatives, explanation, grammar, history)
     - `bot/handlers/admin.py` - Admin panel messages
     - `bot/handlers/payments.py` - Payment success message
     - `bot/handlers/export.py` - Export format selection
   - **Why HTML is better**: Only 3 characters need escaping (`&`, `<`, `>`), compared to 18+ in Markdown. Less prone to breaking user content.

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
- `009_add_show_transcription.sql`: Add `show_transcription` setting to `user_settings` table (IPA feature)
- `010_add_transcription_to_history.sql`: Add `transcription` field to `translation_history` table (IPA storage)

### Important Notes

- ⚠️ **Never delete or modify existing migration files**
- ⚠️ **Never change version numbers of applied migrations**
- ⚠️ **On Railway: migrations MUST be applied manually via `apply_migrations_public.py`**
- ✅ **Always use `IF NOT EXISTS` / `IF EXISTS` for safety**
- ✅ **Always test on dev environment first**
- ✅ **Docker volume `postgres_dev_data` persists data between restarts**

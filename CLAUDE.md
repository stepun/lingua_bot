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

### Multiple Entry Points
- `main.py` - Full aiogram-based bot with all features
- `main_minimal.py` - WSL-compatible version using only stdlib
- `main_fixed.py` - Version with graceful error handling
- `main_simple.py` - Basic functionality version

### Configuration System
All configuration is centralized in `config.py` with environment variable loading. Key models:
- GPT_MODEL = "gpt-4o" (configurable)
- WHISPER_MODEL = "whisper-1"
- Database path, pricing, limits all configurable

### Database Architecture
SQLite-based with async operations in `bot/database.py`:
- User management with subscription tracking
- Daily usage limits and premium features
- Translation history storage
- Payment tracking

## Development Commands

### Local Development
```bash
# Run different bot versions
python main.py                 # Full version (requires all dependencies)
python main_minimal.py         # Minimal version (stdlib only)
python main_fixed.py          # Version with error handling

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_translation.py     # Test translation APIs with timeout
python test_payments.py        # Test payment system
python test_callbacks.py       # Test callback handlers
python test_main_bot.py        # Test main bot functionality
```

### Docker Development
```bash
# Build and run with Docker
docker-compose up --build -d

# Use management scripts
./docker-start.sh              # Interactive menu for Docker management
docker-start.bat              # Windows version

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
- Webhook handling in `bot/handlers/payments.py`
- Subscription management in database layer
- Receipt generation for fiscal compliance (provider_data)

## Docker Architecture

Multi-stage Dockerfile optimized for production:
- Python 3.11 slim base
- Non-root user (linguabot)
- Health checks via SQLite connection test
- Resource limits: 512MB RAM, 0.5 CPU
- Volume mounts for persistent data: `./data`, `./logs`, `./exports`

The Docker setup runs `main.py` (full version) by default, not the minimal version.

## File Structure Notes

- `bot/handlers/` - Message processing and user interactions
- `bot/services/` - Business logic (translation, voice, payments, export)
- `bot/keyboards/` - Telegram UI components
- `bot/middlewares/` - Request processing middleware
- `bot/utils/` - Shared utilities and messages
- `data/` - SQLite database and user data
- `logs/` - Application logs
- `exports/` - Generated PDF/TXT exports

## Remote Server Access

SSH credentials and deployment info are in `creds.md`:
- Server: `ssh vokhma1v@vokhma1v.beget.tech`
- Project path: `/home/v/vokhma1v/vokhma1v.beget.tech/lingua_bot`

### Server Management Scripts
```bash
# Server deployment and management
./start_beget.sh              # Start bot on Beget server
./stop_beget.sh               # Stop bot on server
./status.sh                   # Check bot status
./check_and_restart.sh        # Restart if crashed

# Development/local
./start_bot.sh                # Start bot locally
./start_monitor.sh            # Start with monitoring
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

- `bot_monitor.py` - Process monitoring with auto-restart
- PID tracking in `/tmp/bot.pid` and `/tmp/monitor.pid`
- Automatic health checks and recovery
- Detailed logging in `logs/bot.log` and `logs/monitor.log`

## Testing Infrastructure

The codebase includes several test files:
- Direct API testing with configurable timeouts
- Payment flow verification
- Callback handler validation
- Main bot functionality tests

## Middleware Architecture

- `bot/middlewares/throttling.py` - Rate limiting (configurable in config)
- `bot/middlewares/user_middleware.py` - Automatic user registration
- `bot/middlewares/admin.py` - Admin access control

## Common Issues

1. **Module import errors**: Use `main_minimal.py` for environments without pip/venv
2. **ADMIN_IDS format**: Must be numeric Telegram user ID, not username/URL
3. **Docker not starting**: Ensure Docker Desktop is installed and WSL integration enabled
4. **Translation failures**: Check API keys and account balances, services fail gracefully
5. **Voice TTS errors**:
   - Invalid voice_type (must be: alloy, echo, fable, onyx, nova, shimmer, ash, sage, coral)
   - Check OpenAI API key and ElevenLabs configuration
   - Ensure Telegram voice message permissions are enabled
6. **YooKassa payment errors**: Ensure `need_email=true` and `provider_data` are set for receipt generation
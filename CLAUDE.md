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
```

### Docker Development
```bash
# Build and run with Docker
docker-compose up --build -d

# Use management scripts
./docker-start.sh              # Linux/macOS
docker-start.bat              # Windows

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
- `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY` - For payment processing

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
- YooKassa integration in `bot/services/payment.py`
- Webhook handling in `bot/handlers/payments.py`
- Subscription management in database layer

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

## Common Issues

1. **Module import errors**: Use `main_minimal.py` for environments without pip/venv
2. **ADMIN_IDS format**: Must be numeric Telegram user ID, not username/URL
3. **Docker not starting**: Ensure Docker Desktop is installed and WSL integration enabled
4. **Translation failures**: Check API keys and account balances, services fail gracefully
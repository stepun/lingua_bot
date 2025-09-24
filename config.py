import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot Configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")
    DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

    # Google Cloud
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Payment Configuration
    YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID")
    YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")
    PAYMENT_WEBHOOK_SECRET = os.getenv("PAYMENT_WEBHOOK_SECRET")

    # Telegram Payments
    PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")
    PAYMENT_TEST = os.getenv("PAYMENT_TEST", "false").lower() == "true"

    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")

    # Subscription Prices
    DAILY_PRICE = int(os.getenv("DAILY_PRICE", "100"))
    MONTHLY_PRICE = int(os.getenv("MONTHLY_PRICE", "490"))
    YEARLY_PRICE = int(os.getenv("YEARLY_PRICE", "4680"))

    # Limits
    FREE_DAILY_LIMIT = int(os.getenv("FREE_DAILY_LIMIT", "10"))
    MAX_HISTORY_ITEMS = int(os.getenv("MAX_HISTORY_ITEMS", "100"))

    # Admin Settings
    ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
    ADMIN_IDS = [int(id.strip()) for id in ADMIN_IDS_STR.split(',') if id.strip().isdigit()] if ADMIN_IDS_STR else []
    ADMIN_ID = ADMIN_IDS[0] if ADMIN_IDS else 0  # Primary admin

    # Debug logging for admin configuration
    print(f"[CONFIG DEBUG] ADMIN_IDS environment variable: '{ADMIN_IDS_STR}'")
    print(f"[CONFIG DEBUG] Parsed ADMIN_IDS list: {ADMIN_IDS}")
    print(f"[CONFIG DEBUG] Primary ADMIN_ID: {ADMIN_ID}")

    # Paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    EXPORTS_DIR = BASE_DIR / "exports"
    LOCALES_DIR = BASE_DIR / "locales"

    # Supported Languages
    SUPPORTED_LANGUAGES = {
        'ru': 'Русский',
        'en': 'English',
        'es': 'Español',
        'fr': 'Français',
        'de': 'Deutsch',
        'it': 'Italiano',
        'pt': 'Português',
        'ja': '日本語',
        'zh': '中文',
        'ko': '한국어',
        'ar': 'العربية',
        'hi': 'हिन्दी',
        'tr': 'Türkçe',
        'pl': 'Polski',
        'nl': 'Nederlands',
        'sv': 'Svenska',
        'da': 'Dansk',
        'no': 'Norsk',
        'fi': 'Suomi',
        'cs': 'Čeština',
        'hu': 'Magyar',
        'ro': 'Română',
        'uk': 'Українська',
        'he': 'עברית',
        'th': 'ไทย',
        'vi': 'Tiếng Việt'
    }

    # Translation Styles
    TRANSLATION_STYLES = {
        'informal': 'Неформальный',
        'formal': 'Формальный',
        'business': 'Деловой',
        'travel': 'Для путешествий',
        'academic': 'Академический'
    }

    # Translation Styles (multilingual)
    TRANSLATION_STYLES_MULTILINGUAL = {
        'ru': {
            'informal': 'Неформальный',
            'formal': 'Формальный',
            'business': 'Деловой',
            'travel': 'Для путешествий',
            'academic': 'Академический'
        },
        'en': {
            'informal': 'Informal',
            'formal': 'Formal',
            'business': 'Business',
            'travel': 'Travel',
            'academic': 'Academic'
        }
    }

    # OpenAI Model Configuration
    GPT_MODEL = "gpt-4o"
    WHISPER_MODEL = "whisper-1"

    # Rate Limiting
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX_REQUESTS = 30

    # Voice Settings
    MAX_VOICE_DURATION = 60  # seconds
    SUPPORTED_AUDIO_FORMATS = ['.mp3', '.ogg', '.wav', '.m4a']

    # Export Settings
    PDF_FONT_SIZE = 12
    PDF_PAGE_SIZE = 'A4'

    # Cache Settings
    CACHE_TTL = 3600  # 1 hour

    # Webhook Configuration (for production)
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
    WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
    WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "8080"))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required = ['BOT_TOKEN', 'OPENAI_API_KEY']
        missing = [key for key in required if not getattr(cls, key)]

        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")

        # Create necessary directories
        for dir_path in [cls.DATA_DIR, cls.LOGS_DIR, cls.EXPORTS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)

        return True

config = Config()
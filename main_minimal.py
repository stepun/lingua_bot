#!/usr/bin/env python3
"""
LinguaBot - Минимальная версия для WSL
Использует только стандартные библиотеки Python
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen, Request
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables manually
def load_env():
    env_path = Path(__file__).parent / '.env'
    env_vars = {}

    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

    return env_vars

class SimpleTelegramBot:
    def __init__(self, token, openai_key):
        self.token = token
        self.openai_key = openai_key
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.offset = 0

        # Initialize database
        self.init_db()

    def init_db(self):
        """Initialize simple SQLite database"""
        db_path = Path("data/simple_bot.db")
        db_path.parent.mkdir(exist_ok=True)

        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                translations_today INTEGER DEFAULT 0,
                last_date DATE
            )
        ''')
        self.conn.commit()

    def api_request(self, method, data=None):
        """Make API request to Telegram"""
        url = f"{self.base_url}/{method}"

        if data:
            data = json.dumps(data).encode('utf-8')
            req = Request(url, data=data, headers={'Content-Type': 'application/json'})
        else:
            req = Request(url)

        try:
            with urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    def send_message(self, chat_id, text, reply_markup=None):
        """Send message to chat"""
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            data['reply_markup'] = reply_markup

        return self.api_request('sendMessage', data)

    def translate_with_openai(self, text, target_lang='en'):
        """Translate text using OpenAI API"""
        if not self.openai_key:
            return "❌ OpenAI API ключ не настроен"

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.openai_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': 'gpt-4o',
            'messages': [
                {
                    'role': 'system',
                    'content': f'Переведи следующий текст на {target_lang}. Отвечай только переводом без дополнительных комментариев.'
                },
                {
                    'role': 'user',
                    'content': text
                }
            ],
            'max_tokens': 200,
            'temperature': 0.3
        }

        try:
            data_json = json.dumps(data).encode('utf-8')
            req = Request(url, data=data_json, headers=headers)

            with urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result['choices'][0]['message']['content'].strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"❌ Ошибка перевода: {str(e)}"

    def check_daily_limit(self, user_id):
        """Check user's daily translation limit"""
        today = datetime.now().date()

        cursor = self.conn.execute(
            'SELECT translations_today, last_date FROM users WHERE user_id = ?',
            (user_id,)
        )
        row = cursor.fetchone()

        if not row:
            # New user
            self.conn.execute(
                'INSERT INTO users (user_id, translations_today, last_date) VALUES (?, 0, ?)',
                (user_id, today)
            )
            self.conn.commit()
            return True, 10

        translations_today, last_date = row

        # Reset counter if new day
        if str(last_date) != str(today):
            translations_today = 0
            self.conn.execute(
                'UPDATE users SET translations_today = 0, last_date = ? WHERE user_id = ?',
                (today, user_id)
            )
            self.conn.commit()

        return translations_today < 10, 10 - translations_today

    def increment_translation_count(self, user_id):
        """Increment user's translation count"""
        self.conn.execute(
            'UPDATE users SET translations_today = translations_today + 1 WHERE user_id = ?',
            (user_id,)
        )
        self.conn.commit()

    def handle_message(self, message):
        """Handle incoming message"""
        chat_id = message['chat']['id']
        user = message['from']
        text = message.get('text', '')

        # Save user info
        self.conn.execute(
            'INSERT OR REPLACE INTO users (user_id, username, first_name) VALUES (?, ?, ?)',
            (user['id'], user.get('username'), user.get('first_name'))
        )
        self.conn.commit()

        # Handle commands
        if text.startswith('/start'):
            welcome_text = (
                "🎉 <b>Добро пожаловать в LinguaBot!</b>\n\n"
                "🌍 Я умный переводчик с поддержкой ИИ.\n"
                "Просто отправьте мне любой текст, и я переведу его на английский!\n\n"
                "🆓 Бесплатно: до 10 переводов в день\n\n"
                "Команды:\n"
                "• /help - справка\n"
                "• /status - проверить лимиты"
            )
            self.send_message(chat_id, welcome_text)
            return

        elif text.startswith('/help'):
            help_text = (
                "❓ <b>Справка LinguaBot</b>\n\n"
                "🔸 Отправьте любой текст - получите перевод на английский\n"
                "🔸 /status - проверить оставшиеся переводы\n"
                "🔸 /start - главное меню\n\n"
                "⚠️ Это упрощенная версия для WSL."
            )
            self.send_message(chat_id, help_text)
            return

        elif text.startswith('/status'):
            can_translate, remaining = self.check_daily_limit(user['id'])
            status_text = f"📊 <b>Ваш статус:</b>\n\nОсталось переводов сегодня: {remaining}/10"
            self.send_message(chat_id, status_text)
            return

        # Handle translation
        if text and not text.startswith('/'):
            can_translate, remaining = self.check_daily_limit(user['id'])

            if not can_translate:
                limit_text = (
                    "⚠️ <b>Лимит исчерпан</b>\n\n"
                    "Вы использовали все 10 бесплатных переводов на сегодня.\n"
                    "Попробуйте завтра!"
                )
                self.send_message(chat_id, limit_text)
                return

            # Send "translating" message
            self.send_message(chat_id, "🔄 Перевожу...")

            # Translate
            translation = self.translate_with_openai(text)
            self.increment_translation_count(user['id'])

            response_text = (
                f"🌍 <b>Перевод:</b>\n{translation}\n\n"
                f"📊 Осталось переводов: {remaining - 1}/10"
            )

            self.send_message(chat_id, response_text)

    def get_updates(self):
        """Get updates from Telegram"""
        data = {
            'offset': self.offset,
            'timeout': 30,
            'allowed_updates': ['message']
        }

        response = self.api_request('getUpdates', data)

        if response and response.get('ok'):
            return response.get('result', [])
        return []

    def run(self):
        """Main bot loop"""
        logger.info("🤖 LinguaBot (WSL Simple) is starting...")
        logger.info("✅ Бот запущен! Отправьте /start в Telegram")

        try:
            while True:
                updates = self.get_updates()

                for update in updates:
                    self.offset = update['update_id'] + 1

                    if 'message' in update:
                        try:
                            self.handle_message(update['message'])
                        except Exception as e:
                            logger.error(f"Message handling error: {e}")

        except KeyboardInterrupt:
            logger.info("🛑 Бот остановлен пользователем")
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            self.conn.close()

def main():
    """Main function"""
    # Load environment variables
    env_vars = load_env()

    bot_token = env_vars.get('BOT_TOKEN')
    openai_key = env_vars.get('OPENAI_API_KEY')

    if not bot_token:
        logger.error("❌ BOT_TOKEN не найден в .env файле")
        return

    if not openai_key:
        logger.error("❌ OPENAI_API_KEY не найден в .env файле")
        return

    # Create and run bot
    bot = SimpleTelegramBot(bot_token, openai_key)
    bot.run()

if __name__ == "__main__":
    main()
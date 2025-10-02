# 🌍 LinguaBot - Умный ИИ-переводчик

Telegram-бот для перевода текстов с поддержкой искусственного интеллекта, голосовых сообщений и персональных разговорников.

## 🚀 Возможности

### Бесплатная версия
- ✅ До 10 переводов в день
- ✅ Поддержка 25+ языков
- ✅ Автоопределение языка
- ✅ Базовая озвучка переводов
- ✅ Выбор стиля перевода

### Премиум версия (490₽/мес)
- ⭐ Безлимитные переводы
- 🎤 Голосовой ввод (Whisper AI)
- 🔊 Качественная озвучка (ElevenLabs/OpenAI)
- 📚 История переводов (100 последних)
- 📄 Экспорт в PDF/TXT
- 🔄 Альтернативные варианты перевода
- 📝 Объяснение грамматики
- ⚡ Приоритетная обработка

## 🛠 Технологии

- **Python 3.8+** - основной язык
- **aiogram 3.x** - Telegram Bot API
- **PostgreSQL** - база данных
- **OpenAI GPT-4** - улучшение переводов
- **Whisper API** - распознавание речи
- **DeepL/Yandex** - основные переводчики
- **YooKassa** - обработка платежей
- **ReportLab** - генерация PDF

## 📁 Структура проекта

```
lingua_bot/
├── bot/
│   ├── handlers/          # Обработчики сообщений
│   │   ├── base.py       # Основные команды
│   │   ├── callbacks.py  # Callback-кнопки
│   │   ├── payments.py   # Платежи
│   │   └── export.py     # Экспорт файлов
│   ├── keyboards/        # Клавиатуры
│   │   ├── inline.py     # Inline-кнопки
│   │   └── reply.py      # Reply-кнопки
│   ├── middlewares/      # Middleware
│   │   ├── throttling.py # Ограничение запросов
│   │   └── user_middleware.py # Регистрация пользователей
│   ├── services/         # Бизнес-логика
│   │   ├── translator.py # Сервис переводов
│   │   ├── voice.py      # Работа с голосом
│   │   ├── payment.py    # Платежная система
│   │   └── export.py     # Экспорт данных
│   ├── utils/           # Утилиты
│   │   ├── messages.py  # Тексты сообщений
│   │   └── rate_limit.py # Ограничения
│   └── database.py      # Работа с БД
├── data/                # База данных
├── logs/                # Логи
├── exports/             # Экспортированные файлы
├── config.py            # Конфигурация
├── main.py             # Точка входа
├── requirements.txt    # Зависимости
├── .env.example       # Пример конфигурации
└── README.md          # Документация
```

## ⚙️ Установка и настройка

### 1. Клонирование проекта

```bash
# Перейдите в папку проекта
cd "D:\work\jar\python\tg bots\1\lingua_bot"
```

### 2. Установка зависимостей

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте окружение
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

### 3. Настройка переменных окружения

Скопируйте `.env.example` в `.env` и заполните:

```env
# Telegram Bot (обязательно)
BOT_TOKEN=your_bot_token_from_botfather

# OpenAI API (обязательно)
OPENAI_API_KEY=your_openai_api_key

# Yandex Translate API (рекомендуется)
YANDEX_API_KEY=your_yandex_api_key

# DeepL API (опционально, для лучшего качества)
DEEPL_API_KEY=your_deepl_api_key

# Платежная система YooKassa (для премиум)
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key

# ElevenLabs (опционально, для качественной озвучки)
ELEVENLABS_API_KEY=your_elevenlabs_key

# Админы (ваш Telegram ID)
ADMIN_IDS=your_telegram_user_id
```

### 4. Получение API ключей

#### Telegram Bot Token
1. Откройте [@BotFather](https://t.me/BotFather)
2. Выполните команду `/newbot`
3. Следуйте инструкциям в [BOTFATHER_SETUP.md](BOTFATHER_SETUP.md)

#### OpenAI API Key
1. Зарегистрируйтесь на [OpenAI](https://platform.openai.com)
2. Создайте API ключ в разделе API Keys
3. Пополните баланс для использования GPT-4

#### Yandex Translate API
1. Зарегистрируйтесь в [Yandex Cloud](https://cloud.yandex.com)
2. Создайте сервисный аккаунт
3. Получите API ключ для Translate

#### YooKassa (для платежей)
1. Зарегистрируйтесь на [YooKassa](https://yookassa.ru)
2. Создайте магазин
3. Получите Shop ID и Secret Key

### 5. Запуск бота

```bash
# Запуск в режиме разработки
python main.py

# Запуск в продакшене с логированием
nohup python main.py > bot.log 2>&1 &
```

## 🔧 Конфигурация

### Основные настройки в `config.py`:

- `FREE_DAILY_LIMIT` - лимит бесплатных переводов (по умолчанию: 10)
- `MAX_HISTORY_ITEMS` - размер истории (по умолчанию: 100)
- `MONTHLY_PRICE` - цена месячной подписки (490₽)
- `YEARLY_PRICE` - цена годовой подписки (4680₽)

### Поддерживаемые языки:
Русский, Английский, Испанский, Французский, Немецкий, Итальянский, Португальский, Японский, Китайский, Корейский, Арабский, Хинди, Турецкий, Польский, Нидерландский, Шведский, Датский, Норвежский, Финский, Чешский, Венгерский, Румынский, Украинский, Иврит, Тайский, Вьетнамский

## 🎯 Использование

### Основные команды:
- `/start` - Запуск бота
- `/help` - Справка
- `/language` - Выбор языка перевода
- `/style` - Выбор стиля перевода
- `/settings` - Настройки
- `/premium` - Информация о подписке
- `/history` - История переводов (премиум)

### Стили перевода:
- **Неформальный** - для общения с друзьями
- **Формальный** - для официальных документов
- **Деловой** - для бизнес-переписки
- **Путешествия** - простые фразы для туристов
- **Академический** - для научных текстов

## 🚀 Деплой

### На VPS/Сервере

1. **Установите зависимости системы:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv git
```

2. **Клонируйте проект:**
```bash
git clone <your-repo-url>
cd lingua_bot
```

3. **Настройте окружение:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Создайте systemd сервис:**
```ini
# /etc/systemd/system/linguabot.service
[Unit]
Description=LinguaBot Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/lingua_bot
Environment=PATH=/path/to/lingua_bot/venv/bin
ExecStart=/path/to/lingua_bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

5. **Запустите сервис:**
```bash
sudo systemctl enable linguabot
sudo systemctl start linguabot
sudo systemctl status linguabot
```

### На Render/Railway/Fly.io

1. **Создайте файл для деплоя:**

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

2. **Настройте переменные окружения** на платформе
3. **Деплойте проект** через Git

## 📊 Мониторинг

### Логи
Логи сохраняются в папку `logs/`:
- `bot.log` - основные логи работы
- Уровни: INFO, WARNING, ERROR

### Статистика
Доступна админам через команды:
- Количество пользователей
- Активность по дням
- Доходы от подписок

## 🛡 Безопасность

- **Токены** хранятся в переменных окружения
- **Голосовые файлы** удаляются после обработки
- **История** шифруется для премиум пользователей
- **Rate limiting** предотвращает злоупотребления

## 🐛 Отладка

### Частые проблемы:

**Бот не отвечает:**
- Проверьте правильность токена
- Убедитесь, что бот запущен
- Проверьте логи на ошибки

**Переводы не работают:**
- Проверьте OpenAI API ключ и баланс
- Убедитесь в правильности Yandex API ключа

**Голосовые сообщения не обрабатываются:**
- Проверьте настройки премиум аккаунта
- Убедитесь в наличии всех аудио-библиотек

### Логирование:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Масштабирование

Для больших нагрузок:
1. Используйте Redis для кэширования
2. Настройте балансировщик нагрузки
3. Разделите сервисы по микросервисам
4. Оптимизируйте запросы к PostgreSQL

## 🤝 Поддержка

При возникновении проблем:
1. Проверьте [Issues](https://github.com/your-repo/issues)
2. Создайте новый Issue с описанием проблемы
3. Приложите логи и конфигурацию (без секретных данных)

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

---

**Автор:** AI Assistant
**Версия:** 1.0.0
**Дата:** 2024

🌟 **Не забудьте поставить звезду проекту, если он был полезен!**
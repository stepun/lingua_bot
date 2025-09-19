#!/bin/bash

# 🚀 Автоматическая установка LinguaBot на Beget
# Запустите: bash install_beget.sh

set -e  # Остановить при ошибке

echo "🚀 Начинаю установку LinguaBot на Beget..."
echo "============================================="

# Проверка что мы в правильной папке
if [ ! -f "requirements.txt" ]; then
    echo "❌ ОШИБКА: Файл requirements.txt не найден!"
    echo "Убедитесь что вы в папке lingua_bot"
    echo "Команда: cd lingua_bot && bash install_beget.sh"
    exit 1
fi

echo "✅ Проверка файлов прошла успешно"

# 1. Создание виртуального окружения
echo ""
echo "📦 Создаю виртуальное окружение..."
if [ -d "venv" ]; then
    echo "Папка venv уже существует, удаляю старую..."
    rm -rf venv
fi

python3 -m venv venv
if [ $? -eq 0 ]; then
    echo "✅ Виртуальное окружение создано"
else
    echo "❌ Ошибка создания виртуального окружения"
    exit 1
fi

# 2. Активация окружения и установка зависимостей
echo ""
echo "📚 Устанавливаю зависимости (это займет 2-3 минуты)..."
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Зависимости установлены успешно"
else
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

# 3. Создание необходимых папок
echo ""
echo "📁 Создаю папки для данных..."
mkdir -p data logs exports
chmod 755 data logs exports
echo "✅ Папки созданы"

# 4. Настройка конфигурации
echo ""
echo "⚙️  Настраиваю конфигурацию..."

if [ ! -f ".env" ]; then
    if [ -f ".env.beget" ]; then
        cp .env.beget .env
        echo "✅ Файл .env создан из шаблона"
    else
        echo "❌ Шаблон .env.beget не найден!"
        exit 1
    fi
else
    echo "📝 Файл .env уже существует"
fi

# 5. Интерактивная настройка ключей
echo ""
echo "🔑 НАСТРОЙКА API КЛЮЧЕЙ"
echo "======================="
echo "Для работы бота ОБЯЗАТЕЛЬНО нужны:"
echo "1. Telegram Bot Token"
echo "2. OpenAI API Key"
echo ""

read -p "Хотите настроить ключи сейчас? (y/n): " configure_keys

if [ "$configure_keys" = "y" ] || [ "$configure_keys" = "Y" ]; then
    echo ""
    echo "📋 Введите данные (можно оставить пустым и настроить позже):"

    read -p "Telegram Bot Token: " bot_token
    if [ ! -z "$bot_token" ]; then
        sed -i "s/BOT_TOKEN=.*/BOT_TOKEN=$bot_token/" .env
        echo "✅ Bot Token сохранен"
    fi

    read -p "OpenAI API Key: " openai_key
    if [ ! -z "$openai_key" ]; then
        sed -i "s/OPENAI_API_KEY=.*/OPENAI_API_KEY=$openai_key/" .env
        echo "✅ OpenAI Key сохранен"
    fi

    read -p "Ваш Telegram User ID (для админки): " admin_id
    if [ ! -z "$admin_id" ]; then
        sed -i "s/ADMIN_IDS=.*/ADMIN_IDS=$admin_id/" .env
        echo "✅ Admin ID сохранен"
    fi

    echo ""
    echo "⚠️  Опциональные ключи (для улучшения качества):"

    read -p "Yandex API Key (Enter для пропуска): " yandex_key
    if [ ! -z "$yandex_key" ]; then
        sed -i "s/YANDEX_API_KEY=.*/YANDEX_API_KEY=$yandex_key/" .env
        echo "✅ Yandex Key сохранен"
    fi

    read -p "DeepL API Key (Enter для пропуска): " deepl_key
    if [ ! -z "$deepl_key" ]; then
        sed -i "s/DEEPL_API_KEY=.*/DEEPL_API_KEY=$deepl_key/" .env
        echo "✅ DeepL Key сохранен"
    fi
else
    echo "⚠️  ВАЖНО: Не забудьте настроить .env файл позже!"
    echo "Команда: nano .env"
fi

# 6. Делаем скрипты исполняемыми
echo ""
echo "🔧 Настраиваю права доступа..."
chmod +x start_beget.sh stop_beget.sh install_beget.sh
echo "✅ Права настроены"

# 7. Проверка конфигурации
echo ""
echo "🔍 Проверяю конфигурацию..."

if grep -q "your_bot_token_here" .env; then
    echo "⚠️  Bot Token не настроен"
    TOKEN_OK=false
else
    echo "✅ Bot Token настроен"
    TOKEN_OK=true
fi

if grep -q "your_openai_api_key_here" .env; then
    echo "⚠️  OpenAI Key не настроен"
    OPENAI_OK=false
else
    echo "✅ OpenAI Key настроен"
    OPENAI_OK=true
fi

# 8. Попытка запуска
echo ""
echo "🎯 РЕЗУЛЬТАТ УСТАНОВКИ"
echo "====================="

if [ "$TOKEN_OK" = true ] && [ "$OPENAI_OK" = true ]; then
    echo "✅ Установка завершена успешно!"
    echo ""
    read -p "Запустить бота сейчас? (y/n): " start_now

    if [ "$start_now" = "y" ] || [ "$start_now" = "Y" ]; then
        echo ""
        echo "🚀 Запускаю бота..."
        ./start_beget.sh

        sleep 3
        echo ""
        echo "📊 Проверяю статус..."
        if ps aux | grep -q "[p]ython main.py"; then
            echo "✅ Бот успешно запущен!"
            echo ""
            echo "🎉 ГОТОВО! Ваш бот работает 24/7"
            echo "📱 Найдите бота в Telegram: @PolyglotAI44_bot"
            echo "📝 Логи: tail -f logs/bot.log"
            echo "🛑 Остановка: ./stop_beget.sh"
        else
            echo "❌ Ошибка запуска. Проверьте логи: tail logs/bot.log"
        fi
    else
        echo "✅ Установка завершена. Для запуска выполните: ./start_beget.sh"
    fi
else
    echo "⚠️  Установка завершена, но требуется настройка:"
    echo ""
    if [ "$TOKEN_OK" = false ]; then
        echo "❌ Настройте Bot Token в .env файле"
    fi
    if [ "$OPENAI_OK" = false ]; then
        echo "❌ Настройте OpenAI API Key в .env файле"
    fi
    echo ""
    echo "📝 Для настройки: nano .env"
    echo "🚀 После настройки: ./start_beget.sh"
fi

echo ""
echo "📚 Полная документация: cat BEGET_DEPLOY.md"
echo "============================================="
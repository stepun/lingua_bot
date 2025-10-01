#!/bin/bash

# Скрипт для локальной разработки с PostgreSQL

set -e

echo "🚀 Starting LinguaBot Development Environment..."

# Функция для проверки доступности порта
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        echo "⚠️  Port $1 is already in use. Stopping existing services..."
        docker-compose -f docker-compose.dev.yml down
    fi
}

# Проверка портов
check_port 5433
check_port 8080

# Запуск сервисов
echo "📦 Starting PostgreSQL and LinguaBot..."
docker-compose -f docker-compose.dev.yml up -d postgres

echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Проверка что PostgreSQL запущен
until docker exec linguabot_postgres_dev pg_isready -U linguabot >/dev/null 2>&1; do
    echo "⏳ Waiting for PostgreSQL..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Миграция данных если нужно
if [ -f "/tmp/beget_bot.db" ]; then
    echo "📊 Migrating data from Beget..."
    export DATABASE_URL="postgresql://linguabot:devpassword123@localhost:5433/linguabot"
    python3 migrate_data.py
fi

# Запуск бота
echo "🤖 Starting LinguaBot..."
docker-compose -f docker-compose.dev.yml up -d linguabot

echo ""
echo "✅ Development environment is ready!"
echo ""
echo "📝 Useful commands:"
echo "  View logs:       docker-compose -f docker-compose.dev.yml logs -f"
echo "  Restart bot:     docker-compose -f docker-compose.dev.yml restart linguabot"
echo "  Stop all:        docker-compose -f docker-compose.dev.yml down"
echo "  PostgreSQL CLI:  docker exec -it linguabot_postgres_dev psql -U linguabot -d linguabot"
echo ""
echo "🔗 PostgreSQL: postgresql://linguabot:devpassword123@localhost:5433/linguabot"
echo "🔗 Bot Webhook: http://localhost:8080/webhook"
echo "🔗 Admin Panel: http://localhost:8080/admin"

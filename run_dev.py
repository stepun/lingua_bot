#!/usr/bin/env python3
"""
Скрипт для быстрой локальной разработки с PostgreSQL в Docker
Запускает только PostgreSQL в контейнере, бот локально через Python
"""

import os
import sys
import subprocess
import time

def check_docker():
    """Проверка что Docker запущен"""
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
        return True
    except:
        print("❌ Docker не запущен или не установлен")
        print("   Установите Docker Desktop: https://www.docker.com/products/docker-desktop")
        return False

def start_postgres():
    """Запуск PostgreSQL в Docker"""
    print("🐘 Starting PostgreSQL...")

    # Проверка существующего контейнера
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", "name=linguabot_postgres_dev", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )

    if "linguabot_postgres_dev" in result.stdout:
        print("📦 PostgreSQL container already exists, starting...")
        subprocess.run(["docker", "start", "linguabot_postgres_dev"])
    else:
        print("📦 Creating new PostgreSQL container...")
        subprocess.run([
            "docker", "run", "-d",
            "--name", "linguabot_postgres_dev",
            "-e", "POSTGRES_DB=linguabot",
            "-e", "POSTGRES_USER=linguabot",
            "-e", "POSTGRES_PASSWORD=devpassword123",
            "-p", "5433:5432",
            "postgres:15-alpine"
        ])

    # Ожидание готовности
    print("⏳ Waiting for PostgreSQL to be ready...")
    for i in range(30):
        result = subprocess.run(
            ["docker", "exec", "linguabot_postgres_dev", "pg_isready", "-U", "linguabot"],
            capture_output=True
        )
        if result.returncode == 0:
            print("✅ PostgreSQL is ready!")
            return True
        time.sleep(1)

    print("❌ PostgreSQL failed to start")
    return False

def setup_env():
    """Настройка переменных окружения для локальной разработки"""
    # Загружаем .env.local если существует
    env_local = ".env.local"
    if os.path.exists(env_local):
        print(f"📝 Loading {env_local}...")
        from dotenv import load_dotenv
        load_dotenv(env_local, override=True)
    else:
        # Устанавливаем минимальные переменные
        os.environ["DATABASE_URL"] = "postgresql://linguabot:devpassword123@localhost:5433/linguabot"
        os.environ["PORT"] = "0"  # Polling mode

    print("✅ Environment configured")
    print(f"   DATABASE_URL: {os.environ.get('DATABASE_URL', 'not set')}")
    print(f"   BOT_TOKEN: {os.environ.get('BOT_TOKEN', 'not set')[:20]}...")

def run_bot():
    """Запуск бота"""
    print("\n🤖 Starting LinguaBot...")
    print("   Press Ctrl+C to stop\n")

    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Stopping bot...")

def main():
    print("🚀 LinguaBot Development Environment")
    print("=" * 50)

    if not check_docker():
        sys.exit(1)

    if not start_postgres():
        sys.exit(1)

    setup_env()

    print("\n" + "=" * 50)
    print("📝 Useful commands:")
    print("   PostgreSQL CLI:  docker exec -it linguabot_postgres_dev psql -U linguabot -d linguabot")
    print("   Stop PostgreSQL: docker stop linguabot_postgres_dev")
    print("   Remove all:      docker rm -f linguabot_postgres_dev")
    print("=" * 50 + "\n")

    run_bot()

if __name__ == "__main__":
    main()

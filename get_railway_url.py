#!/usr/bin/env python3
"""
Скрипт для получения Railway URL проекта
"""

import os
import sys
import requests
import json
from pathlib import Path

def get_railway_url():
    """Получить URL Railway проекта"""

    # Попробуем получить из переменных окружения Railway
    railway_urls = [
        os.getenv("RAILWAY_STATIC_URL"),
        os.getenv("RAILWAY_PUBLIC_URL"),
        os.getenv("RAILWAY_PRIVATE_URL"),
        os.getenv("PUBLIC_URL"),
        os.getenv("RAILWAY_SERVICE_URL")
    ]

    for url in railway_urls:
        if url:
            print(f"✅ Найден Railway URL: {url}")
            return url

    # Если не нашли в переменных, попробуем определить по паттерну
    project_name = "lingua-bot"
    possible_urls = [
        f"https://{project_name}-production.up.railway.app",
        f"https://lingua-bot-production.up.railway.app",
        f"https://linguabot-production.up.railway.app",
        f"https://web-production.up.railway.app",
        f"https://python-railway-template-production.up.railway.app"
    ]

    print("🔍 Проверяем возможные URL...")
    for url in possible_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 404, 502]:  # 502 означает что сервис существует но не отвечает
                print(f"✅ Найден рабочий URL: {url}")
                return url
        except:
            continue

    print("❌ Не удалось найти Railway URL автоматически")
    return None

def generate_webhook_host():
    """Сгенерировать случайный Railway URL"""
    import random
    import string

    # Генерируем случайный ID как у Railway
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    suggested_urls = [
        f"https://lingua-bot-production-{random_id}.up.railway.app",
        f"https://linguabot-production-{random_id}.up.railway.app",
        f"https://web-production-{random_id}.up.railway.app"
    ]

    print("💡 Предполагаемые URL для вашего проекта:")
    for url in suggested_urls:
        print(f"   {url}")

    return suggested_urls[0]

def main():
    print("🚂 Поиск Railway URL для lingua_bot...\n")

    # Проверяем переменные окружения
    print("📍 Проверка переменных окружения Railway:")
    env_vars = [
        "RAILWAY_STATIC_URL",
        "RAILWAY_PUBLIC_URL",
        "RAILWAY_PRIVATE_URL",
        "PUBLIC_URL",
        "RAILWAY_SERVICE_URL",
        "PORT"
    ]

    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: не установлена")

    print("\n" + "="*60 + "\n")

    # Попытка найти URL
    railway_url = get_railway_url()

    if railway_url:
        print(f"🎯 WEBHOOK_HOST для Railway:")
        print(f"   {railway_url}")
        print(f"\n📋 Добавьте в Railway Variables:")
        print(f"   Key: WEBHOOK_HOST")
        print(f"   Value: {railway_url}")

        print(f"\n🔗 URL для веб-хука в ЮКассе:")
        print(f"   {railway_url}/webhook/yookassa")

    else:
        print("🔄 Генерируем возможные URL...")
        suggested_url = generate_webhook_host()

        print(f"\n📝 Попробуйте использовать:")
        print(f"   WEBHOOK_HOST: {suggested_url}")
        print(f"   Веб-хук ЮКасса: {suggested_url}/webhook/yookassa")

        print(f"\n💭 Как найти точный URL:")
        print(f"   1. Railway Dashboard → ваш проект")
        print(f"   2. Кликните на сервис → справа будет URL")
        print(f"   3. Или Deployments → Latest → кнопка с доменом")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Поиск реального Railway URL для проекта
"""

import requests
import time

def test_url(url, timeout=5):
    """Тестирует URL на доступность"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code, response.text[:200]
    except Exception as e:
        return None, str(e)

def main():
    print("🔍 Поиск рабочего Railway URL...\n")

    # Возможные варианты URL для проекта lingua_bot
    possible_urls = [
        # Стандартные варианты
        "https://lingua-bot-production.up.railway.app",
        "https://linguabot-production.up.railway.app",
        "https://lingua-bot.up.railway.app",
        "https://linguabot.up.railway.app",

        # С различными суффиксами
        "https://web-production.up.railway.app",
        "https://main-production.up.railway.app",
        "https://app-production.up.railway.app",
        "https://bot-production.up.railway.app",

        # С кодами проекта
        "https://lingua-bot-production-3.up.railway.app",
        "https://lingua-bot-production-1.up.railway.app",
        "https://lingua-bot-production-2.up.railway.app",

        # Другие варианты
        "https://python-railway-template-production.up.railway.app",
        "https://telegram-bot-production.up.railway.app",
        "https://translation-bot-production.up.railway.app"
    ]

    working_urls = []

    for url in possible_urls:
        print(f"Тестирую: {url}")
        status, response = test_url(url)

        if status:
            if status == 200:
                print(f"  ✅ {status} - РАБОТАЕТ!")
                working_urls.append((url, status, response))
            elif status in [404, 502, 503]:
                print(f"  🟡 {status} - Сервис существует, но не отвечает")
                working_urls.append((url, status, response))
            else:
                print(f"  ⚠️  {status} - Неожиданный ответ")
                working_urls.append((url, status, response))
        else:
            print(f"  ❌ Недоступен: {response}")

        time.sleep(0.5)  # Небольшая пауза между запросами

    print("\n" + "="*60)

    if working_urls:
        print("\n🎯 Найденные URL:")
        for url, status, response in working_urls:
            print(f"\nURL: {url}")
            print(f"Статус: {status}")
            if "OK" in response or "health" in response.lower():
                print("📈 Отвечает на health check!")
            if response:
                print(f"Ответ: {response}")
    else:
        print("\n❌ Ни один URL не найден")
        print("\n💡 Возможные решения:")
        print("1. Проект еще не задеплоен в Railway")
        print("2. Нужно создать новый проект в Railway")
        print("3. Проект находится под другим именем")
        print("4. Нужно подождать завершения деплоя")

if __name__ == "__main__":
    main()
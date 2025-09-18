#!/usr/bin/env python3
"""
Поиск URL для конкретного Railway проекта
"""

import requests
import time

def test_url(url):
    try:
        response = requests.get(url, timeout=10)
        return response.status_code, response.text[:300]
    except Exception as e:
        return None, str(e)

def main():
    project_id = "522a489e-3bbd-409f-a4b5-01dd2c20a91d"
    service_id = "6308e44f-7998-4480-9f48-dced1ebedbed"

    print(f"🔍 Поиск URL для Railway проекта: {project_id[:8]}...")
    print(f"📦 Service ID: {service_id[:8]}...\n")

    # Возможные URL для вашего конкретного проекта
    possible_urls = [
        # Стандартные паттерны Railway с ID
        f"https://web-production-{service_id[:8]}.up.railway.app",
        f"https://app-production-{service_id[:8]}.up.railway.app",
        f"https://service-production-{service_id[:8]}.up.railway.app",
        f"https://lingua-bot-production-{service_id[:8]}.up.railway.app",

        # С project ID
        f"https://web-production-{project_id[:8]}.up.railway.app",
        f"https://app-production-{project_id[:8]}.up.railway.app",

        # Общие варианты
        "https://web-production.up.railway.app",
        "https://lingua-bot-production.up.railway.app",

        # С полными ID (редко, но возможно)
        f"https://{service_id}.up.railway.app",
        f"https://{project_id}.up.railway.app"
    ]

    working_urls = []

    for url in possible_urls:
        print(f"Тестирую: {url}")
        status, response = test_url(url)

        if status:
            if status == 200:
                print(f"  ✅ {status} - РАБОТАЕТ!")
                if "OK" in response or "health" in response:
                    print(f"  📈 Health check работает!")
                working_urls.append((url, status, "WORKING"))
            elif status in [404, 502]:
                if "Application not found" in response:
                    print(f"  ❌ {status} - Application not found")
                else:
                    print(f"  🟡 {status} - Сервис существует")
                    working_urls.append((url, status, "EXISTS"))
            else:
                print(f"  ⚠️  {status}")
                working_urls.append((url, status, "OTHER"))
        else:
            print(f"  ❌ Недоступен")

        time.sleep(0.3)

    print("\n" + "="*70)

    if working_urls:
        print("\n🎯 Результаты:")
        for url, status, type in working_urls:
            if type == "WORKING":
                print(f"✅ РАБОЧИЙ URL: {url}")
            elif type == "EXISTS":
                print(f"🟡 Сервис существует: {url}")

    if not any(t[2] == "WORKING" for t in working_urls):
        print("\n💡 Возможные причины:")
        print("1. Приложение еще деплоится")
        print("2. Есть ошибки в коде или зависимостях")
        print("3. Не настроены переменные окружения")
        print("4. Неправильный порт")

        print("\n🔧 Что делать:")
        print("1. В Railway → Deployments → посмотреть логи")
        print("2. Убедиться что BOT_TOKEN и другие переменные установлены")
        print("3. Проверить что статус деплоя 'Success'")

if __name__ == "__main__":
    main()
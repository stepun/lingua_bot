#!/usr/bin/env python3
"""
Диагностика Railway проблем
"""

import os
import sys
import traceback

def check_environment():
    """Проверка переменных окружения"""
    print("🔍 Проверка переменных окружения Railway...\n")

    required_vars = [
        "BOT_TOKEN",
        "PORT"
    ]

    optional_vars = [
        "OPENAI_API_KEY",
        "YOOKASSA_SHOP_ID",
        "YOOKASSA_SECRET_KEY",
        "WEBHOOK_HOST",
        "RAILWAY_STATIC_URL",
        "RAILWAY_PUBLIC_URL"
    ]

    print("📋 Обязательные переменные:")
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: установлена ({len(value)} символов)")
        else:
            print(f"  ❌ {var}: НЕ УСТАНОВЛЕНА")
            missing_required.append(var)

    print("\n📋 Дополнительные переменные:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value[:50]}...")
        else:
            print(f"  ⚪ {var}: не установлена")

    if missing_required:
        print(f"\n❌ КРИТИЧНО: Отсутствуют обязательные переменные: {', '.join(missing_required)}")
        return False
    else:
        print(f"\n✅ Все обязательные переменные установлены")
        return True

def check_imports():
    """Проверка импортов"""
    print("\n🔍 Проверка импортов...\n")

    modules = [
        ("aiogram", "Telegram Bot API"),
        ("aiohttp", "HTTP сервер"),
        ("openai", "OpenAI API"),
        ("yookassa", "ЮКасса API"),
        ("aiosqlite", "База данных"),
        ("python-dotenv", "Переменные окружения")
    ]

    failed_imports = []

    for module, description in modules:
        try:
            __import__(module.replace("-", "_"))
            print(f"  ✅ {module}: {description}")
        except ImportError as e:
            print(f"  ❌ {module}: НЕ НАЙДЕН - {description}")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n❌ Отсутствуют модули: {', '.join(failed_imports)}")
        print("💡 Проверьте requirements.txt и установку зависимостей")
        return False
    else:
        print(f"\n✅ Все модули доступны")
        return True

def check_bot_token():
    """Проверка токена бота"""
    print("\n🔍 Проверка токена бота...\n")

    token = os.getenv("BOT_TOKEN")
    if not token:
        print("❌ BOT_TOKEN не установлен")
        return False

    # Проверка формата токена
    if ":" not in token:
        print("❌ BOT_TOKEN имеет неверный формат")
        print("💡 Должен быть вида: 1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi")
        return False

    bot_id, bot_hash = token.split(":", 1)

    if not bot_id.isdigit():
        print("❌ Bot ID должен содержать только цифры")
        return False

    if len(bot_hash) < 30:
        print("❌ Bot hash слишком короткий")
        return False

    print(f"✅ Токен корректен (Bot ID: {bot_id})")
    return True

def test_bot_connection():
    """Тест подключения к Telegram API"""
    print("\n🔍 Тест подключения к Telegram...\n")

    try:
        from aiogram import Bot
        import asyncio

        async def test_bot():
            token = os.getenv("BOT_TOKEN")
            if not token:
                return False, "Токен не установлен"

            try:
                bot = Bot(token=token)
                me = await bot.get_me()
                await bot.session.close()
                return True, f"Бот @{me.username} ({me.first_name})"
            except Exception as e:
                return False, str(e)

        result, info = asyncio.run(test_bot())

        if result:
            print(f"✅ Подключение успешно: {info}")
            return True
        else:
            print(f"❌ Ошибка подключения: {info}")
            return False

    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def check_port():
    """Проверка порта"""
    print("\n🔍 Проверка порта...\n")

    port = os.getenv("PORT", "8080")

    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            print(f"✅ Порт корректен: {port_num}")
            return True
        else:
            print(f"❌ Порт вне допустимого диапазона: {port_num}")
            return False
    except ValueError:
        print(f"❌ Порт не является числом: {port}")
        return False

def main():
    print("🚂 Railway Диагностика PolyglotAI44\n")
    print("="*50)

    checks = [
        ("Переменные окружения", check_environment),
        ("Импорты модулей", check_imports),
        ("Порт", check_port),
        ("Токен бота", check_bot_token),
        ("Подключение к Telegram", test_bot_connection)
    ]

    results = []

    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка в проверке '{name}': {e}")
            traceback.print_exc()
            results.append((name, False))

    print("\n" + "="*50)
    print("📊 ИТОГИ ДИАГНОСТИКИ:\n")

    passed = 0
    for name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ОШИБКА"
        print(f"{status}: {name}")
        if result:
            passed += 1

    print(f"\nРезультат: {passed}/{len(results)} проверок пройдено")

    if passed == len(results):
        print("\n🎉 Все проверки пройдены! Приложение должно работать.")
    else:
        print(f"\n⚠️ Найдены проблемы. Исправьте их и попробуйте снова.")
        print("\n💡 Рекомендации:")
        print("1. Установите недостающие переменные в Railway")
        print("2. Проверьте requirements.txt")
        print("3. Убедитесь что BOT_TOKEN правильный")

if __name__ == "__main__":
    main()
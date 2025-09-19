#!/bin/bash

# Скрипт для остановки бота на Beget

echo "Останавливаю бота..."

# Убиваем процесс по PID если файл существует
if [ -f "bot.pid" ]; then
    BOT_PID=$(cat bot.pid)
    if kill -0 $BOT_PID 2>/dev/null; then
        kill $BOT_PID
        echo "Бот остановлен (PID: $BOT_PID)"
        rm bot.pid
    else
        echo "Процесс с PID $BOT_PID не найден"
        rm bot.pid
    fi
else
    # Если файла PID нет, ищем по имени процесса
    pkill -f "python.*main"
    pkill -f "python3.*main"
    echo "Процессы бота остановлены"
fi

# Дополнительная проверка и остановка всех процессов
pkill -f "main_fixed_middleware.py"
pkill -f "main_no_middleware.py"
pkill -f "main_debug.py"
pkill -f "test_main_bot.py"
pkill -f "test_polling.py"

echo "✅ Бот полностью остановлен"
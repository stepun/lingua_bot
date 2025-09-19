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
    pkill -f "python main.py"
    echo "Процессы бота остановлены"
fi

echo "Бот полностью остановлен"
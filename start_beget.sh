#!/bin/bash

# Скрипт для запуска бота на Beget
# Поместите этот файл в корень проекта на сервере

# Переходим в директорию проекта
cd ~/lingua_bot

# Активируем виртуальное окружение
source venv/bin/activate

# Проверяем существование папки данных
if [ ! -d "data" ]; then
    mkdir data
    echo "Создана папка data"
fi

# Проверяем существование папки логов
if [ ! -d "logs" ]; then
    mkdir logs
    echo "Создана папка logs"
fi

# Проверяем существование .env файла
if [ ! -f ".env" ]; then
    echo "ОШИБКА: Файл .env не найден!"
    echo "Скопируйте .env.beget в .env и заполните переменные"
    exit 1
fi

# Убиваем предыдущий процесс если он запущен
pkill -f "python main.py"

# Запускаем бота в фоне
nohup python main.py > logs/bot.log 2>&1 &

# Получаем PID процесса
BOT_PID=$!
echo "Бот запущен с PID: $BOT_PID"
echo $BOT_PID > bot.pid

echo "Логи можно посмотреть командой: tail -f logs/bot.log"
echo "Для остановки используйте: pkill -f 'python main.py'"
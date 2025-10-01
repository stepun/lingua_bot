# 🚀 Быстрый старт локальной разработки

## 1. Установите Docker Desktop
https://www.docker.com/products/docker-desktop

## 2. Скопируйте репозиторий
```bash
cd /mnt/w/work/KWORK/vokhma440/lingua_bot
```

## 3. Запустите локальное окружение
```bash
python3 run_dev.py
```

Скрипт автоматически:
- ✅ Запустит PostgreSQL в Docker
- ✅ Загрузит .env.local с настройками
- ✅ Запустит бота с тестовым токеном

## 4. Тестируйте в Telegram

Найдите бота по токену и отправьте `/start`

## Файлы конфигурации

**`.env.local`** - локальные настройки (уже настроен):
- Тестовый бот: `8246111868:AAHBCPejWEuyfiGReDKecZXkFOQgnXG_UdI`
- PostgreSQL: `localhost:5433`
- Polling mode (без webhook)

**Основной `.env`** используется на Railway (production)

## Полезное

**Админка локально:**
```
http://localhost:8080/admin?user_id=120962578
```

**PostgreSQL CLI:**
```bash
docker exec -it linguabot_postgres_dev psql -U linguabot
```

**Остановить:**
```bash
# Ctrl+C в консоли бота
docker stop linguabot_postgres_dev
```

## Workflow

1. **Запуск:** `python3 run_dev.py`
2. **Тест** изменений локально
3. **Коммит:** `git add . && git commit -m "..."`
4. **Push:** `git push` (Railway автоматически задеплоит production)

---

Подробнее: **DEV_README.md**

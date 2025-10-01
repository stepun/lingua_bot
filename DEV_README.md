# 🚀 Локальная Разработка

Быстрая настройка локального окружения для разработки с PostgreSQL.

## Способ 1: Только PostgreSQL в Docker (рекомендуется)

Запускает PostgreSQL в Docker, бот локально через Python:

```bash
python3 run_dev.py
```

**Преимущества:**
- ✅ Мгновенный перезапуск при изменениях кода
- ✅ Легкая отладка в IDE
- ✅ Не нужно пересобирать Docker образ

## Способ 2: Всё в Docker

Полная Docker-среда с PostgreSQL и ботом:

```bash
# Linux/macOS
./dev.sh

# Или вручную
docker-compose -f docker-compose.dev.yml up -d
```

**Просмотр логов:**
```bash
docker-compose -f docker-compose.dev.yml logs -f linguabot
```

**Остановка:**
```bash
docker-compose -f docker-compose.dev.yml down
```

## PostgreSQL подключение

**Локальное:**
```
postgresql://linguabot:devpassword123@localhost:5433/linguabot
```

**CLI:**
```bash
docker exec -it linguabot_postgres_dev psql -U linguabot -d linguabot
```

## Миграция данных с Beget

После запуска PostgreSQL:

```bash
export DATABASE_URL="postgresql://linguabot:devpassword123@localhost:5433/linguabot"
python3 migrate_data.py
```

## Полезные команды

**Очистка базы:**
```sql
docker exec -it linguabot_postgres_dev psql -U linguabot -d linguabot -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

**Пересоздание таблиц:**
```bash
# Запустите бота один раз - он создаст таблицы автоматически
python3 run_dev.py
```

**Остановка PostgreSQL:**
```bash
docker stop linguabot_postgres_dev
```

**Удаление всех данных:**
```bash
docker rm -f linguabot_postgres_dev
docker volume rm linguabot_postgres_dev_data
```

## Workflow

1. **Запуск:** `python3 run_dev.py`
2. **Изменение кода** - бот автоматически не перезапускается
3. **Перезапуск:** Ctrl+C и снова `python3 run_dev.py`
4. **Тестирование** на локальной БД
5. **Коммит:** `git add . && git commit -m "..."`
6. **Push:** `git push` - Railway автоматически задеплоит

## Различия с Railway

| Параметр | Локально | Railway |
|----------|----------|---------|
| PostgreSQL | localhost:5433 | hopper.proxy.rlwy.net:52905 |
| Webhook | Отключен (polling) | Включен |
| Админка | http://localhost:8080/admin | https://linguabot-vokhma440.up.railway.app/admin |
| Логи | В консоли | Railway Dashboard |

## Отладка

**Проблемы с Docker:**
```bash
# Проверка Docker
docker info

# Логи PostgreSQL
docker logs linguabot_postgres_dev
```

**Проблемы с подключением:**
```bash
# Проверка порта
lsof -i :5433

# Проверка контейнера
docker ps | grep postgres
```

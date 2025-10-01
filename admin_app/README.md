# LinguaBot Admin Panel

Telegram Mini App для администрирования LinguaBot переводчика.

## Возможности

- 📊 **Dashboard** - статистика бота в реальном времени
  - Общее количество пользователей
  - Премиум подписчики
  - Активность за сегодня
  - Статистика переводов
  - Анализ популярности языков

- 👥 **Управление пользователями**
  - Поиск пользователей
  - Просмотр детальной информации
  - Выдача премиум доступа
  - Фильтрация по статусу

- 📝 **Логи и мониторинг**
  - История переводов
  - Системные логи
  - Логи ошибок
  - Фильтрация по типу

## Установка

1. Установите зависимости:
```bash
pip install fastapi uvicorn
```

2. Запустите админ-панель:
```bash
# Linux/macOS
./start_admin.sh

# Windows
start_admin.bat
```

3. Админ панель будет доступна на `http://localhost:8081`

## Настройка в Telegram

1. Добавьте переменную окружения в `.env`:
```
ADMIN_PANEL_URL=https://your-domain.com:8081
```

2. В Telegram боте используйте команду `/admin_panel` для открытия панели

## Архитектура

### Backend (FastAPI)
- `app.py` - главное приложение FastAPI
- `auth.py` - авторизация через Telegram WebApp
- `api/stats.py` - API статистики
- `api/users.py` - API управления пользователями
- `api/logs.py` - API логов

### Frontend (Telegram Mini App)
- `static/index.html` - структура интерфейса
- `static/style.css` - стили (адаптивный дизайн)
- `static/app.js` - логика приложения

## Безопасность

- Авторизация через Telegram WebApp InitData
- Проверка подписи запросов от Telegram
- Доступ только для администраторов из `ADMIN_IDS`
- HTTPS обязателен для production

## Development

```bash
# Запуск с hot reload
cd lingua_bot
python -m uvicorn admin_app.app:app --reload --port 8081

# Проверка API
curl http://localhost:8081/health
```

## Production deployment

1. Используйте HTTPS (обязательно для Telegram WebApp)
2. Настройте reverse proxy (nginx/caddy)
3. Используйте systemd для автозапуска
4. Настройте firewall для порта 8081

### Пример nginx config:
```nginx
server {
    listen 443 ssl;
    server_name admin.yourbot.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8081;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API Documentation

После запуска доступна интерактивная документация:
- Swagger UI: `http://localhost:8081/docs`
- ReDoc: `http://localhost:8081/redoc`

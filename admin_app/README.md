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
pip install aiohttp
```

2. Запустите админ-панель:
```bash
# Linux/macOS
./start_admin.sh

# Windows
start_admin.bat
```

3. Админ панель будет доступна на `http://localhost:8080`

## Настройка в Telegram

1. Добавьте переменную окружения в `.env`:
```
ADMIN_PANEL_URL=https://your-domain.com:8080
```

2. В Telegram боте используйте команду `/admin` для открытия панели

## Архитектура

### Backend (aiohttp)
- `app.py` - главное приложение на aiohttp
- `auth.py` - авторизация через Telegram WebApp
- Все API endpoints определены внутри `setup_admin_routes()`

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
# Запуск через главный скрипт (запускает бот + админку)
python main.py

# Проверка API
curl http://localhost:8080/api/stats/
```

## Production deployment

1. Используйте HTTPS (обязательно для Telegram WebApp)
2. Настройте reverse proxy (nginx/caddy)
3. Используйте systemd для автозапуска
4. Настройте firewall для порта 8080

### Пример nginx config:
```nginx
server {
    listen 443 ssl;
    server_name admin.yourbot.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## API Endpoints

Основные endpoints:
- `GET /api/stats/` - общая статистика
- `GET /api/stats/daily?days=7` - статистика по дням
- `GET /api/stats/languages` - статистика по языкам
- `GET /api/stats/performance` - метрики производительности
- `GET /api/users/` - список пользователей
- `GET /api/users/{user_id}/history` - история переводов пользователя
- `POST /api/users/{user_id}/block` - заблокировать пользователя
- `POST /api/users/{user_id}/unblock` - разблокировать пользователя
- `GET /api/logs/translations` - логи переводов
- `GET /api/feedback` - список feedback
- `POST /api/feedback/{feedback_id}/status` - обновить статус feedback

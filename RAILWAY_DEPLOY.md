# Деплой LinguaBot на Railway

## Пошаговая инструкция

### 1. Подготовка проекта
Все необходимые файлы для Railway уже созданы:
- `Procfile` - команда запуска
- `railway.toml` - конфигурация Railway
- `runtime.txt` - версия Python
- `.env.railway` - шаблон переменных окружения

### 2. Создание аккаунта на Railway
1. Перейдите на [railway.app](https://railway.app)
2. Зарегистрируйтесь через GitHub
3. Подтвердите email

### 3. Создание нового проекта
1. Нажмите "New Project"
2. Выберите "Deploy from GitHub repo"
3. Подключите ваш GitHub аккаунт (если не подключен)
4. Выберите репозиторий с lingua_bot

### 4. Настройка переменных окружения
1. В панели Railway откройте ваш проект
2. Перейдите в раздел "Variables"
3. Добавьте следующие обязательные переменные:

```bash
# Обязательные
BOT_TOKEN=your_bot_token_from_botfather
OPENAI_API_KEY=your_openai_api_key

# Рекомендуемые (для лучшего качества переводов)
YANDEX_API_KEY=your_yandex_api_key
DEEPL_API_KEY=your_deepl_api_key

# Админ (ваш Telegram ID)
ADMIN_IDS=your_telegram_user_id

# Автоматические (не меняйте)
DATABASE_PATH=/tmp/data/bot.db
PYTHONUNBUFFERED=1
PYTHONPATH=/app
```

### 5. Получение необходимых API ключей

#### Telegram Bot Token:
1. Напишите @BotFather в Telegram
2. Создайте нового бота: `/newbot`
3. Получите токен

#### OpenAI API Key:
1. Перейдите на [platform.openai.com](https://platform.openai.com)
2. Зарегистрируйтесь и войдите
3. Перейдите в API Keys
4. Создайте новый ключ

#### Yandex API Key (опционально):
1. Перейдите на [cloud.yandex.ru](https://cloud.yandex.ru)
2. Создайте аккаунт и проект
3. Подключите Yandex Translate API
4. Получите API ключ

#### Ваш Telegram ID:
1. Напишите @userinfobot в Telegram
2. Получите ваш числовой ID

### 6. Деплой
1. Railway автоматически начнет деплой после коммита
2. Следите за логами в разделе "Deployments"
3. Процесс займет 2-5 минут

### 7. Проверка работы
1. После успешного деплоя найдите ваш бот в Telegram
2. Отправьте `/start`
3. Попробуйте перевести текст

## Управление ботом

### Просмотр логов
```bash
# В Railway Dashboard -> Deployments -> View Logs
```

### Перезапуск бота
```bash
# В Railway Dashboard -> Deployments -> Redeploy
```

### Обновление кода
```bash
# Просто сделайте git push - Railway автоматически пересоберет
git add .
git commit -m "Update bot"
git push origin main
```

## Устранение проблем

### Бот не отвечает
1. Проверьте логи в Railway
2. Убедитесь, что BOT_TOKEN правильный
3. Проверьте, что переменные окружения установлены

### Ошибки API
1. Проверьте OPENAI_API_KEY
2. Убедитесь, что у вас есть кредиты на OpenAI
3. Проверьте лимиты API

### Проблемы с базой данных
1. База создается автоматически в /tmp/data/
2. При перезапуске данные могут быть потеряны (это нормально для бесплатного плана)

## Стоимость
- Railway предоставляет $5 бесплатных кредитов в месяц
- Этого хватит для тестирования и небольшого использования
- При превышении лимита нужно будет добавить платежную карту

## Альтернативы
Если Railway не подходит, рассмотрите:
- Render.com
- PythonAnywhere
- Heroku
- Fly.io
# 🐳 Docker Setup для LinguaBot

## Установка Docker

### Windows

1. **Скачайте Docker Desktop:**
   - Перейдите на [docker.com](https://www.docker.com/products/docker-desktop)
   - Скачайте Docker Desktop for Windows
   - Запустите установку

2. **Настройка WSL 2:**
   - Docker Desktop автоматически настроит WSL 2
   - Убедитесь что WSL 2 включен в настройках Docker

3. **Проверка установки:**
   ```bash
   docker --version
   docker-compose --version
   ```

### Linux/macOS

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# macOS (с Homebrew)
brew install docker docker-compose
```

## 🚀 Запуск бота в Docker

### Способ 1: Через скрипт (рекомендуется)

**Windows:**
```bash
cd "D:\work\jar\python\tg bots\1\lingua_bot"
docker-start.bat
```

**Linux/macOS:**
```bash
cd "/path/to/lingua_bot"
./docker-start.sh
```

### Способ 2: Команды напрямую

```bash
# Перейти в папку проекта
cd "D:\work\jar\python\tg bots\1\lingua_bot"

# Построить и запустить
docker-compose up --build -d

# Посмотреть логи
docker-compose logs -f

# Остановить
docker-compose down
```

## 🔧 Основные команды Docker

### Управление контейнерами

```bash
# Построить образ
docker-compose build

# Запустить в фоне
docker-compose up -d

# Запустить с пересборкой
docker-compose up --build -d

# Остановить
docker-compose down

# Остановить и удалить volumes
docker-compose down -v
```

### Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Логи в реальном времени
docker-compose logs -f linguabot

# Логи последние 100 строк
docker-compose logs --tail=100 linguabot

# Войти в контейнер
docker exec -it linguabot /bin/bash
```

### Отладка

```bash
# Проверить health check
docker inspect linguabot --format="{{.State.Health.Status}}"

# Посмотреть ресурсы
docker stats linguabot

# Проверить переменные окружения
docker exec linguabot env
```

## 📊 Мониторинг и логи

### Структура логов

```
logs/
├── bot.log          # Основные логи
├── errors.log       # Ошибки
└── access.log       # Доступ к API
```

### Просмотр логов

```bash
# Все логи
docker-compose logs linguabot

# Только ошибки
docker-compose logs linguabot | grep ERROR

# Фильтр по времени
docker-compose logs --since="2024-01-01T00:00:00" linguabot
```

## 🔄 Обновление бота

```bash
# 1. Остановить текущую версию
docker-compose down

# 2. Получить новый код (если используете git)
git pull

# 3. Пересобрать с обновлениями
docker-compose build --no-cache

# 4. Запустить обновленную версию
docker-compose up -d
```

## 🗂️ Volumes и данные

### Постоянные данные

```
./data/          → /home/linguabot/app/data/
./logs/          → /home/linguabot/app/logs/
./exports/       → /home/linguabot/app/exports/
```

### Резервное копирование

```bash
# Создать архив данных
tar -czf linguabot-backup-$(date +%Y%m%d).tar.gz data/ logs/

# Восстановить из архива
tar -xzf linguabot-backup-20240101.tar.gz
```

## 🛠️ Troubleshooting

### Проблема: Container не запускается

```bash
# Проверить логи
docker-compose logs linguabot

# Проверить конфигурацию
docker-compose config

# Пересобрать без кэша
docker-compose build --no-cache
```

### Проблема: Нет доступа к API

1. Проверьте `.env` файл
2. Убедитесь что токены правильные
3. Проверьте сетевые подключения

```bash
# Проверить переменные окружения
docker exec linguabot env | grep -E "(BOT_TOKEN|OPENAI_API_KEY)"

# Тест сетевого подключения
docker exec linguabot curl -s https://api.telegram.org/bot$BOT_TOKEN/getMe
```

### Проблема: Высокое потребление ресурсов

```bash
# Мониторинг ресурсов
docker stats linguabot

# Настройка лимитов в docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 256M
      cpus: '0.5'
```

## 🌍 Production деплой

### Готовность к продакшену

1. **Настройте reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:8080;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Настройте SSL (Let's Encrypt):**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Мониторинг (Portainer):**
   Раскомментируйте секцию portainer в docker-compose.yml

4. **Автозапуск:**
   ```bash
   # Добавить в systemd
   sudo systemctl enable docker
   ```

## 📈 Масштабирование

### Горизонтальное масштабирование

```yaml
# docker-compose.yml
services:
  linguabot:
    deploy:
      replicas: 3
```

### Добавление PostgreSQL

Раскомментируйте секцию postgres в docker-compose.yml

### Добавление Redis

Раскомментируйте секцию redis в docker-compose.yml

---

## ✅ Готово!

Docker конфигурация создана и готова к использованию. Используйте скрипты `docker-start.bat` или `docker-start.sh` для удобного управления!
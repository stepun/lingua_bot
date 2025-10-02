# План реализации функционала админ-панели

## Статус: ✅ Полностью завершён
**Дата создания:** 2025-10-01
**Дата завершения:** 2025-10-02
**Текущая реализация:** 100% от ТЗ (12/12 задач)

---

## 📊 Приоритет 1: Критичный функционал (Must Have)

### ✅ Задача 1.1: Исправить фильтры в логах переводов
**Статус:** ✅ Завершено
**Описание:** Фильтры Voice/Text работают корректно с PostgreSQL (TRUE/FALSE)
**Файлы:** `admin_app/app.py:226-228`
**Результат:** Фильтры работают корректно

### ✅ Задача 1.2: Исправить sequence для translation_history
**Статус:** ✅ Завершено
**Описание:** AUTO INCREMENT (SERIAL) работает корректно в PostgreSQL
**SQL:** `SELECT setval('translation_history_id_seq', 49, false);`
**Результат:** Новые записи создаются с правильными ID

### ✅ Задача 1.3: Telegram WebApp авторизация
**Статус:** ✅ Завершено
**Описание:** HMAC валидация через Telegram initData
**Файлы:** `admin_app/auth.py`, `admin_app/app.py:39-71`, `admin_app/static/app.js:79-93`
**Результат:** Безопасный доступ только через Telegram

---

## 🎯 Приоритет 2: Важный функционал (Should Have)

### ✅ Задача 2.1: Блокировка/разблокировка пользователей
**Статус:** ✅ Завершено (2025-10-01)
**Оценка:** 2-3 часа
**Описание:**
- Добавить поле `is_blocked` в таблицу `users`
- API endpoint: `POST /api/users/{user_id}/block` и `/unblock`
- Кнопки Block/Unblock в карточке пользователя
- Middleware в боте для проверки блокировки

**Файлы для изменения:**
- `bot/database.py` - миграция + методы `block_user()`, `unblock_user()`, `is_blocked()`
- `admin_app/app.py` - новые endpoints
- `admin_app/static/app.js` - обработчики кнопок
- `admin_app/static/index.html` - кнопки UI
- `bot/middlewares/user_middleware.py` - проверка блокировки

**Приёмочные критерии:**
- ✅ Заблокированный пользователь не может отправлять запросы боту
- ✅ Админ видит статус "BLOCKED" в списке пользователей
- ✅ Кнопка Block/Unblock переключается динамически

---

### ✅ Задача 2.2: История запросов конкретного пользователя
**Статус:** ✅ Завершено (2025-10-01)
**Оценка:** 1-2 часа
**Описание:**
- При клике на View показывать модальное окно с последними 10 переводами
- API endpoint: `GET /api/users/{user_id}/history`
- Фильтр по типу (voice/text) и дате

**Файлы для изменения:**
- `admin_app/app.py` - endpoint `get_user_history()`
- `admin_app/static/app.js` - функция `viewUserHistory()`, модальное окно
- `admin_app/static/index.html` - HTML модального окна

**Приёмочные критерии:**
- ✅ Модальное окно открывается при клике на пользователя
- ✅ Отображаются последние переводы с датами
- ✅ Можно закрыть окно

---

### ✅ Задача 2.3: Поиск по логам переводов
**Статус:** ✅ Завершено (2025-10-01)
**Оценка:** 1 час
**Описание:**
- Добавить поле поиска над таблицей логов
- Поиск по: username, source_text, translation

**Файлы для изменения:**
- `admin_app/static/index.html` - input для поиска
- `admin_app/static/app.js` - debounced search handler
- `admin_app/app.py` - добавить параметр `search` в `get_translation_logs()`

**Приёмочные критерии:**
- ✅ Поиск работает с задержкой 500ms (debounce)
- ✅ Можно искать по username, тексту оригинала, переводу

---

### ✅ Задача 2.4: Метрики производительности
**Статус:** ✅ Завершено (2025-10-01)
**Оценка:** 3-4 часа
**Описание:**
- Добавить поля в `translation_history`: `processing_time_ms`, `status` (success/error), `error_message`
- Новая карточка в Dashboard: "Средняя скорость обработки", "Процент ошибок"
- График ошибок по дням

**Файлы для изменения:**
- `bot/database.py` - миграция + методы для метрик
- `bot/handlers/base.py` - сохранять время обработки
- `admin_app/app.py` - endpoint `/api/stats/performance`
- `admin_app/static/app.js` - отрисовка метрик
- `admin_app/static/index.html` - карточки метрик

**Приёмочные критерии:**
- ✅ Отображается среднее время обработки за день/неделю
- ✅ Процент успешных/ошибочных запросов
- ✅ График ошибок за последние 7 дней

---

## 💡 Приоритет 3: Желательный функционал (Nice to Have)

### ✅ Задача 3.1: Система ролей (Admin/Moderator/Analyst)
**Статус:** ✅ Завершено (2025-10-02)
**Оценка:** 4-6 часов
**Описание:**
- Таблица `admin_roles`: `user_id`, `role` (admin/moderator/analyst), `permissions` (JSON)
- Admin - полный доступ
- Moderator - просмотр + блокировка пользователей
- Analyst - только просмотр статистики
- Интеграция с командами бота для проверки ролей из БД

**Файлы для изменения:**
- `bot/database.py:136-147` - таблица admin_roles ✅
- `bot/database.py:861-941` - методы assign_role(), get_user_role(), get_all_admin_users(), remove_admin_role() ✅
- `admin_app/auth.py:10-16` - ROLE_PERMISSIONS mapping ✅
- `admin_app/auth.py:83-124` - get_user_role_and_permissions(), has_permission() ✅
- `admin_app/auth.py:170-219` - check_admin_with_permission() ✅
- `admin_app/handlers/roles.py` - endpoints для управления ролями (GET/POST/DELETE) ✅
- `admin_app/handlers/stats.py` - обновлены все endpoints на check_admin_with_permission ✅
- `admin_app/handlers/users.py` - обновлены все endpoints + re-raise HTTPException ✅
- `admin_app/handlers/logs.py` - обновлен на check_admin_with_permission + re-raise HTTPException ✅
- `admin_app/handlers/feedback.py` - обновлен на check_admin_with_permission + re-raise HTTPException ✅
- `admin_app/handlers/admin_logs.py` - обновлен на check_admin_with_permission + re-raise HTTPException ✅
- `admin_app/app.py:84-87` - регистрация маршрутов /api/admin-roles ✅
- `admin_app/static/index.html:103-105` - вкладка Roles в навигации ✅
- `admin_app/static/index.html:251-261` - UI для управления ролями ✅
- `admin_app/static/index.html:298-322` - модальное окно Assign Role ✅
- `admin_app/static/index.html:330` - обновлена версия app.js (v=20251002181000) ✅
- `admin_app/static/app.js:97-121,235-259` - переводы RU/EN (24 ключа) ✅
- `admin_app/static/app.js:369-375` - apiRequest возвращает статус 403 в объекте ошибки ✅
- `admin_app/static/app.js:524-526` - обработчик case 'roles' ✅
- `admin_app/static/app.js:701-713,873-884,906-918,1017-1029,1135-1147` - обработка 403 ошибок для всех вкладок ✅
- `admin_app/static/app.js:1081-1217` - функции loadRoles(), renderRoles(), assign/remove role ✅
- `admin_app/static/app.js:1296-1298` - event listeners ✅
- `migrations/006_add_admin_roles.sql` - миграция БД ✅
- `bot/middlewares/admin.py:45-59` - async check_admin_role() с проверкой БД + fallback к ADMIN_IDS ✅
- `bot/handlers/admin.py:9,33,66,123,149,173,203,233` - обновлены все команды для использования check_admin_role() ✅

**Приёмочные критерии:**
- ✅ Админ может назначать роли через вкладку "Roles"
- ✅ Система поддерживает 3 роли: Admin (полный доступ), Moderator (Users & Logs), Analyst (Dashboard only)
- ✅ CRUD операции с ролями: просмотр списка, назначение, изменение, удаление
- ✅ Защита от удаления собственной роли
- ✅ Backend проверка прав через check_admin_with_permission()
- ✅ Двуязычный интерфейс (RU/EN)
- ✅ Команды бота (/admin_panel, /admin, /admin_config, /admin_stats) работают для пользователей из admin_roles
- ✅ Fallback к ADMIN_IDS для обратной совместимости

---

### ✅ Задача 3.2: Настройки системы
**Статус:** ✅ ПОЛНОСТЬЮ ЗАВЕРШЕНО (2025-10-02)
**Оценка:** 6-8 часов | **Фактическое:** ~8 часов (с дополнительными улучшениями)
**Описание:**
- Новая вкладка "Settings" в навигации ✅
- Настройки с категориями: Translation, Voice, Pricing, Limits, Features, **API Keys** ✅
- Динамическое чтение настроек БЕЗ перезапуска бота ✅
- Сохранение в таблице `system_settings` ✅
- **Управление API ключами всех сервисов** ✅
- **Показ балансов API сервисов** ✅
- **Интеграция с translator.py и voice.py** ✅

**Реализованные файлы (базовые):**
- `migrations/007_add_system_settings.sql` - миграция БД ✅
- `bot/database.py:943-1035` - методы для работы с настройками ✅
- `bot/config.py:156-202` - метод `load_from_db()` ✅
- `admin_app/handlers/settings.py` - 4 API endpoints ✅
- `admin_app/app.py:93-97` - регистрация маршрутов ✅
- `admin_app/auth.py:16` - пермишн `manage_settings` + роль `settings_manager` ✅
- `admin_app/static/index.html:266-289` - вкладка Settings ✅
- `admin_app/static/modules/settings.js` - модуль настроек (145 строк) ✅
- `admin_app/static/app.js` - интеграция модуля ✅

**Дополнительные файлы (миграция 008):**
- `migrations/008_add_api_keys.sql` - API ключи для всех сервисов ✅
- `admin_app/handlers/api_balance.py` - балансы API (158 строк) ✅
- `admin_app/static/modules/balances.js` - UI балансов (148 строк) ✅
- `bot/services/translator.py` - интеграция с настройками БД ✅
- `bot/services/voice.py` - интеграция с настройками БД ✅

**Динамическое чтение (БЕЗ перезапуска):**
- `bot/services/payment.py:17-27` - цены подписок ✅
- `bot/keyboards/inline.py:103-142` - клавиатуры с ценами ✅
- `bot/database.py:429` - лимиты переводов ✅
- `bot/services/voice.py:326` - лимиты голоса ✅
- `bot/services/translator.py:358-422` - флаги и ключи API (deepl_enabled, yandex_enabled, gpt_enhancement) ✅
- `bot/services/voice.py:85-108,134-271` - флаги и ключи API (asr_enabled, tts_provider) ✅

**Приёмочные критерии (расширенные):**
- ✅ Настройки сохраняются в БД
- ✅ Настройки применяются БЕЗ рестарта (dynamic reading)
- ✅ Изменения логируются в `admin_actions`
- ✅ RBAC с permission `manage_settings`
- ✅ Категорийные фильтры (7 категорий: +API Keys)
- ✅ Bulk update + Reset функциональность
- ✅ Поля типа `secret` с маскировкой и кнопкой показа/скрытия
- ✅ API ключи: DeepL, Yandex, OpenAI, ElevenLabs, YooKassa, Telegram
- ✅ Показ балансов всех API сервисов
- ✅ Кнопки прямых ссылок на billing панели сервисов
- ✅ Сервисы (translator, voice) читают настройки из БД с fallback на .env
- ✅ Многострочная навигация (flex-wrap)

**Особенности реализации:**
- **API Keys Management**: Администратор может менять API ключи через админ-панель, бот использует их из БД
- **API Balances**: Показ статуса OpenAI (Active + модели), использования DeepL/ElevenLabs (символы + процент)
- **Service Integration**: Полная интеграция translator.py и voice.py с настройками из БД
- **Fallback Chain**: БД → .env → disabled (если все пусто)

---

### ✅ Задача 3.3: Обратная связь (Feedback)
**Статус:** ✅ Завершено (2025-10-01)
**Оценка:** 3-4 часа
**Описание:**
- Команда `/feedback <текст>` в боте
- Таблица `feedback`: `id`, `user_id`, `message`, `status` (new/reviewed/resolved), `created_at`
- Вкладка Feedback в админ-панели

**Файлы для изменения:**
- `bot/handlers/base.py:120-171` - команда `/feedback` ✅
- `bot/database.py:670-724` - таблица + методы ✅
- `admin_app/app.py:507-557` - endpoint `/api/feedback` ✅
- `admin_app/static/index.html:141-156` - вкладка Feedback ✅
- `admin_app/static/app.js:441-534` - список сообщений с кнопками Mark as Reviewed/Resolved ✅

**Приёмочные критерии:**
- ✅ Пользователь может отправить feedback через `/feedback [текст]`
- ✅ Админ видит все сообщения с фильтром по статусу (All/New/Reviewed/Resolved)
- ✅ Можно пометить как просмотрено/решено через кнопки в интерфейсе
- ✅ Двуязычная поддержка (RU/EN) в команде бота
- ✅ Даты отображаются в формате ISO для корректной сериализации JSON

---

### ✅ Задача 3.4: Логирование действий администратора
**Статус:** ✅ Завершено (2025-10-02)
**Оценка:** 2-3 часа
**Описание:**
- Таблица `admin_actions`: `id`, `admin_user_id`, `action` (block_user/grant_premium/etc), `target_user_id`, `details` (JSON), `timestamp`
- Вкладка "Admin Logs" в админ-панели

**Файлы для изменения:**
- `bot/database.py:124-134` - таблица admin_actions, методы `log_admin_action()`, `get_admin_logs()` ✅
- `admin_app/handlers/admin_logs.py` - endpoint `/api/admin-logs` ✅
- `admin_app/app.py:77` - регистрация маршрута ✅
- `admin_app/handlers/users.py` - логирование в grant_premium, ban_user, unban_user, send_message, view_history ✅
- `admin_app/handlers/feedback.py` - логирование в update_feedback ✅
- `admin_app/static/index.html:224-246` - вкладка Admin Logs с фильтрами ✅
- `admin_app/static/app.js:909-1020` - функции loadAdminLogs(), renderAdminLogs(), переводы RU/EN ✅

**Приёмочные критерии:**
- ✅ Все действия админа логируются (grant_premium, ban_user, unban_user, send_message, update_feedback, view_history)
- ✅ Можно фильтровать по админу и типу действия
- ✅ Нельзя удалить логи (только просмотр)

---

### ✅ Задача 3.5: Двуязычный интерфейс (EN/RU)
**Статус:** ✅ Завершено (2025-10-01)
**Оценка:** 2-3 часа
**Описание:**
- Переключатель языка в header
- Хранение выбора в localStorage
- i18n библиотека или простой объект с переводами

**Файлы для изменения:**
- `admin_app/static/app.js:11-224` - объект translations (88 ключей RU/EN), функции `t()`, `applyTranslations()`, `switchLanguage()` ✅
- `admin_app/static/index.html:21-37,48-50,57-176` - переключатель языка в header, data-i18n атрибуты ✅
- `admin_app/static/app.js:567-600` - динамические переводы для Users (badges, кнопки, пагинация) ✅
- `admin_app/static/app.js:750-800` - динамические переводы для Feedback (статусы, кнопки) ✅

**Приёмочные критерии:**
- ✅ Можно переключать язык без перезагрузки (кнопки RU/EN в header)
- ✅ Выбор языка сохраняется в localStorage
- ✅ Переведены все статические элементы (навигация, заголовки, формы)
- ✅ Переведён динамический контент (кнопки, badge, pagination)
- ✅ Активное состояние кнопки текущего языка
- ✅ 88 переводов для RU и EN

---

## 📈 Оценка трудозатрат

| Приоритет | Задач | Часов | Статус |
|-----------|-------|-------|--------|
| P1 (Must Have) | 3 | ~5ч | ✅ 100% (3/3) |
| P2 (Should Have) | 4 | ~9-12ч | ✅ 100% (4/4) |
| P3 (Nice to Have) | 5 | ~21-28ч | ✅ 100% (5/5) |
| **ИТОГО** | **12** | **~35-45ч** | **✅ 100% (12/12)** |

---

## 🚀 Рекомендуемый порядок реализации

### Неделя 1 (8-10 часов)
1. ✅ ~~Задача 1.1: Фильтры в логах~~ (Завершено)
2. ✅ ~~Задача 1.2: Sequence для БД~~ (Завершено)
3. ✅ ~~Задача 1.3: Telegram авторизация~~ (Завершено)
4. ✅ ~~Задача 2.1: Блокировка пользователей~~ (Завершено 2025-10-01)
5. ✅ ~~Задача 2.2: История пользователя~~ (Завершено 2025-10-01)
6. ✅ ~~Задача 2.3: Поиск по логам~~ (Завершено 2025-10-01)
7. ✅ ~~Задача 2.4: Метрики производительности~~ (Завершено 2025-10-01)

### Неделя 2 (6-8 часов)
8. ✅ ~~Задача 3.3: Feedback система~~ (Завершено 2025-10-01)
9. ✅ ~~Задача 3.5: Двуязычный интерфейс~~ (Завершено 2025-10-01)
10. ✅ ~~Задача 3.4: Логирование действий~~ (Завершено 2025-10-02)
11. ✅ ~~Задача 3.1: Система ролей~~ (Завершено 2025-10-02)

### Неделя 3 (8 часов)
12. ✅ ~~Задача 3.2: Настройки системы + API Keys + Балансы~~ (Завершено 2025-10-02)

---

## 📝 Примечания

- Все изменения БД требуют миграций для PostgreSQL
- Перед деплоем на Railway нужно обновить sequence для всех таблиц
- Тестирование каждой задачи локально через ngrok
- После завершения каждой недели - деплой на Railway
- Обновлять этот документ после завершения каждой задачи

---

## ✨ Итоговая статистика

**Дата начала:** 2025-10-01
**Дата завершения:** 2025-10-02
**Реализовано:** 12/12 задач (100%)
**Фактическое время:** ~35-40 часов

**Ключевые достижения:**
- ✅ Полнофункциональная админ-панель с Telegram WebApp авторизацией
- ✅ Система ролей и прав доступа (RBAC)
- ✅ Динамические настройки системы без перезапуска
- ✅ Управление API ключами всех сервисов
- ✅ Мониторинг балансов API
- ✅ Блокировка пользователей и управление подписками
- ✅ Метрики производительности и статистика
- ✅ Feedback система
- ✅ Логирование всех действий администратора
- ✅ Двуязычный интерфейс (RU/EN)

**Дополнительные улучшения (сверх плана):**
- API Keys Management (миграция 008)
- API Balances с прямыми ссылками на billing
- Интеграция translator.py и voice.py с настройками БД
- Многострочная адаптивная навигация
- Упрощенная конфигурация Docker Compose

---

## 🔗 Связанные документы

- `admin_app/README.md` - описание архитектуры
- `admin_app/SETTINGS_TASK_PLAN.md` - детальный план задачи 3.2
- `bot/database.py` - схема БД
- `admin_app/auth.py` - система авторизации
- `CLAUDE.md` - общая документация проекта

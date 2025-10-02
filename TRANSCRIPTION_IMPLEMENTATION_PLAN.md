# План реализации фонетической транскрипции (IPA)

## Статус: ✅ Реализовано

## Описание задачи
Добавление отображения фонетической транскрипции (IPA - International Phonetic Alphabet) для переводов.

## Требования
- ✅ Транскрипция для **точного перевода** (basic_translation), НЕ для стилизованного
- ✅ Только для **премиум-пользователей**
- ✅ По умолчанию **выключена**
- ✅ Генерация через **GPT-4o**
- ✅ Формат отображения: один сообщение, транскрипция после точного перевода
- ✅ Сохранение в историю переводов
- ✅ Отображение в экспорте (PDF/TXT)

## Выполненные миграции

### Migration 009: Настройка пользователя
```sql
ALTER TABLE user_settings ADD COLUMN IF NOT EXISTS show_transcription BOOLEAN DEFAULT FALSE;
```
**Статус:** ✅ Применена (локально и на Railway)

### Migration 010: Сохранение в истории
```sql
ALTER TABLE translation_history ADD COLUMN IF NOT EXISTS transcription TEXT;
```
**Статус:** ✅ Применена локально, ⏳ требуется применить на Railway

## Измененные файлы

### 1. Database Layer
**Файл:** `bot/database.py`
- ✅ Добавлено `'show_transcription'` в `valid_settings`
- ✅ Добавлено `s.show_transcription` в SELECT запрос `get_user()`
- ✅ Добавлен параметр `transcription` в `add_translation_history()`
- ✅ Добавлено поле в INSERT запрос истории

### 2. UI - Настройки
**Файл:** `bot/keyboards/inline.py`
- ✅ Добавлена кнопка "📝 Показывать транскрипцию" (только для премиум)
- ✅ Отображение статуса: "✅ Вкл" / "❌ Выкл"

**Файл:** `bot/handlers/callbacks.py`
- ✅ Добавлено `'show_transcription': 'Транскрипция'` в `setting_names`

### 3. Translation Service
**Файл:** `bot/services/translator.py`
- ✅ Модифицирован system_prompt для запроса IPA
- ✅ Модифицирован user_prompt с явным указанием использовать basic_translation
- ✅ Добавлен парсинг поля `Transcription:` из ответа GPT
- ✅ Транскрипция включена в результат (metadata)

**Критичные инструкции в промпте:**
```
IMPORTANT: Create IPA transcription for the BASIC translation ONLY: "{translated_text}"
NOT for the enhanced/styled version!
```

### 4. Display Handlers
**Файл:** `bot/handlers/base.py`

#### Text Translation Handler (строка ~457):
```python
if 'basic_translation' in metadata:
    response_text += f"📝 *Точный перевод:*\n{metadata['basic_translation']}\n"

    # Транскрипция после точного перевода
    if (user_info.get('is_premium', False) and
        user_info.get('show_transcription', False) and
        metadata.get('transcription')):
        response_text += f"🗣️ {metadata['transcription']}\n"

    response_text += f"\n✨ *Стилизованный перевод ({style_display}):*\n{translated}"
```

#### Voice Handler (строка ~282):
```python
if 'basic_translation' in metadata and user_info.get('is_premium', False):
    response_text += f"📝 *Точный перевод:*\n{metadata['basic_translation']}\n"

    # Транскрипция после точного перевода
    if (user_info.get('show_transcription', False) and
        metadata.get('transcription')):
        response_text += f"🗣️ {metadata['transcription']}\n"

    response_text += f"\n✨ *Улучшенный перевод ({style_display}):*\n{translated}"
```

#### История переводов:
- ✅ Строка 255 (voice_handler): добавлен `transcription=metadata.get('transcription')`
- ✅ Строка 409 (text_translation_handler): добавлен `transcription=metadata.get('transcription')`

### 5. Export Service
**Файл:** `bot/services/export.py`

#### PDF Export (строки 186-205):
```python
translation_parts = [
    f"<b>{voice_icon}🔸 {source_lang} → {target_lang}</b> ({time_str})",
    f"<i>Оригинал:</i> {source_text}"
]

# Точный перевод
if basic_translation:
    translation_parts.append(f"<i>Точный перевод:</i> {basic_translation}")

# Транскрипция
if transcription:
    translation_parts.append(f"<i>Транскрипция:</i> {transcription}")

# Стилизованный перевод
translation_parts.append(f"<i>Стилизованный перевод:</i> {translated_text}")

translation_text = "<br/>".join(translation_parts)
```

#### TXT Export (строки 319-333):
```python
content.append(f"{voice_icon}🔸 {source_lang} → {target_lang} ({time_str})")
content.append(f"   Оригинал: {source_text}")

# Точный перевод
if basic_translation:
    content.append(f"   Точный перевод: {basic_translation}")

# Транскрипция
if transcription:
    content.append(f"   Транскрипция: {transcription}")

# Стилизованный перевод
content.append(f"   Стилизованный перевод: {translated_text}")
```

## Формат отображения

### В чате бота:
```
📝 Точный перевод:
Hello

🗣️ [həˈləʊ]

✨ Стилизованный перевод (неформальный):
Hey there!
```

### В экспорте (PDF/TXT):
```
🔸 Русский → English (18:52)
   Оригинал: Привет
   Точный перевод: Hello
   Транскрипция: [həˈləʊ]
   Стилизованный перевод: Hey there!
```

## Проблемы и решения

### 1. ❌ Настройка не переключалась
- **Причина:** `show_transcription` не в списке `valid_settings`
- **Решение:** Добавлено в `database.py:valid_settings`

### 2. ❌ Поле не извлекалось из БД
- **Причина:** Не было в SELECT запросе `get_user()`
- **Решение:** Добавлен `s.show_transcription` в SELECT

### 3. ❌ GPT генерировал транскрипцию для улучшенного перевода
- **Причина:** Недостаточно четкий промпт
- **Решение:** Добавлены IMPORTANT теги и явное указание текста для транскрипции

### 4. ❌ Экспорт не показывал транскрипцию
- **Причина:** Поля не обрабатывались в export.py
- **Решение:** Добавлена обработка `basic_translation` и `transcription`

## Оставшиеся задачи

1. ⏳ **Применить миграцию 010 на Railway:**
   ```bash
   python3 apply_migrations_public.py
   ```

2. ✅ **Тестирование:**
   - Включение/выключение настройки
   - Генерация IPA для точного перевода
   - Отображение в чате
   - Сохранение в историю
   - Экспорт PDF/TXT

## Команды для проверки

### Локальная БД:
```bash
# Проверить миграции
docker exec linguabot_postgres_dev psql -U linguabot -d linguabot -c "SELECT * FROM schema_migrations;"

# Проверить настройки пользователя
docker exec linguabot_postgres_dev psql -U linguabot -d linguabot -c "SELECT user_id, show_transcription FROM user_settings WHERE user_id = YOUR_USER_ID;"

# Проверить историю с транскрипцией
docker exec linguabot_postgres_dev psql -U linguabot -d linguabot -c "SELECT id, source_text, basic_translation, transcription FROM translation_history ORDER BY created_at DESC LIMIT 5;"
```

### Railway БД:
```bash
# Применить миграции
python3 apply_migrations_public.py
```

## Технические детали

### GPT Prompt Structure:
```
System: "5. Phonetic transcription (IPA) for the BASIC translation (not enhanced)"

User: "IMPORTANT: Create IPA transcription for the BASIC translation ONLY: '{translated_text}'
NOT for the enhanced/styled version!

Format:
Transcription: [IPA for '{translated_text}' ONLY, e.g. [həˈləʊ]]"
```

### Database Schema:
```sql
-- user_settings table
show_transcription BOOLEAN DEFAULT FALSE

-- translation_history table
transcription TEXT
```

### Data Flow:
```
1. User sends message
2. Translation service gets basic translation
3. GPT generates IPA for basic translation
4. IPA stored in metadata['transcription']
5. Display handler shows IPA if setting enabled
6. IPA saved to database in translation_history
7. Export includes IPA in output files
```

## Дата завершения
2025-10-02

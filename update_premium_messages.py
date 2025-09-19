#!/usr/bin/env python3
"""
Скрипт для обновления всех премиум сообщений с кнопками оплаты
"""

import re

def update_callbacks_file():
    file_path = '/mnt/d/work/jar/python/tg_bots/lingua_bot/bot/handlers/callbacks.py'

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find premium checks with callback.answer
    pattern = r'if not user_info\.get\(\'is_premium\'\):\s*\n\s*await callback\.answer\([^)]+\).*?\s*\n\s*return'

    replacement = '''if not user_info.get('is_premium'):
        await callback.message.edit_text(
            get_text('premium_required', user_info.get('interface_language', 'ru')),
            reply_markup=get_premium_keyboard(),
            parse_mode='Markdown'
        )
        await callback.answer()
        return'''

    # Count replacements
    matches = re.findall(pattern, content, re.MULTILINE)
    print(f"Found {len(matches)} premium checks to update")

    # Replace all occurrences
    new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Updated {len(matches)} premium messages with payment buttons")

    return len(matches)

if __name__ == "__main__":
    count = update_callbacks_file()
    if count > 0:
        print("\n🎯 All premium messages now include direct payment buttons!")
    else:
        print("\n⚠️ No changes made - patterns might have changed")
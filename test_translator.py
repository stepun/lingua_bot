#!/usr/bin/env python3
"""Test script to check if translation works"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.services.translator import TranslatorService

async def test_translation():
    """Test translation functionality"""
    print("🧪 Testing translation service...")

    # Test cases
    test_cases = [
        ("Hello world", "ru", "English to Russian"),
        ("Привет мир", "fr", "Russian to French"),
        ("Bonjour le monde", "es", "French to Spanish"),
        ("Hola mundo", "de", "Spanish to German"),
    ]

    async with TranslatorService() as translator:
        for text, target_lang, description in test_cases:
            print(f"\n📝 {description}:")
            print(f"   Input: {text}")
            print(f"   Target: {target_lang}")

            try:
                result, metadata = await translator.translate(
                    text=text,
                    target_lang=target_lang,
                    style='informal',
                    enhance=False  # Don't use GPT enhancement for basic test
                )

                if result:
                    print(f"   ✅ Result: {result}")
                    print(f"   📊 Source detected: {metadata.get('source_lang', 'unknown')}")
                else:
                    print(f"   ❌ Translation failed: {metadata.get('error', 'Unknown error')}")

            except Exception as e:
                print(f"   💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_translation())
#!/usr/bin/env python3
"""Test translation service with timeout"""

import asyncio
import os
import logging
from dotenv import load_dotenv
import aiohttp
from openai import AsyncOpenAI

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openai_direct():
    """Test direct OpenAI API call"""
    print("\n=== Testing OpenAI API directly ===")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        return False

    try:
        client = AsyncOpenAI(
            api_key=api_key,
            timeout=10.0  # 10 second timeout
        )

        print("Sending test request to OpenAI...")
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator."},
                {"role": "user", "content": "Translate to English: Привет мир"}
            ],
            max_tokens=100,
            temperature=0.3
        )

        result = response.choices[0].message.content
        print(f"✅ OpenAI response: {result}")
        return True

    except asyncio.TimeoutError:
        print("❌ OpenAI request timed out!")
        return False
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

async def test_translation_service():
    """Test translation service from bot"""
    print("\n=== Testing Bot Translation Service ===")

    try:
        from bot.services.translator import TranslatorService

        async with TranslatorService() as translator:
            print("Translating test text...")
            result = await asyncio.wait_for(
                translator.translate(
                    text="Привет мир",
                    target_lang="en",
                    source_lang="ru"
                ),
                timeout=15.0
            )
            print(f"✅ Translation result: {result}")
            return True

    except asyncio.TimeoutError:
        print("❌ Translation service timed out!")
        return False
    except Exception as e:
        print(f"❌ Translation error: {e}")
        return False

async def test_network():
    """Test basic network connectivity"""
    print("\n=== Testing Network ===")

    try:
        async with aiohttp.ClientSession() as session:
            # Test Google
            async with session.get("https://google.com", timeout=5) as resp:
                print(f"✅ Google.com: {resp.status}")

            # Test OpenAI API endpoint
            async with session.get("https://api.openai.com/v1/models", timeout=5) as resp:
                print(f"✅ OpenAI API endpoint: {resp.status}")

        return True
    except Exception as e:
        print(f"❌ Network error: {e}")
        return False

async def main():
    print("🔍 TRANSLATION SERVICE DIAGNOSTICS")
    print("=" * 40)

    # Test network
    network_ok = await test_network()

    if network_ok:
        # Test OpenAI
        openai_ok = await test_openai_direct()

        # Test translation service
        translation_ok = await test_translation_service()

        print("\n" + "=" * 40)
        print("📊 RESULTS:")
        print(f"Network: {'✅' if network_ok else '❌'}")
        print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
        print(f"Translation Service: {'✅' if translation_ok else '❌'}")

        if not openai_ok:
            print("\n⚠️ RECOMMENDATIONS:")
            print("1. Check OPENAI_API_KEY in .env")
            print("2. Check OpenAI account balance")
            print("3. Try using a VPN if API is blocked")
            print("4. Check firewall settings")
    else:
        print("\n❌ Network issues detected. Check internet connection.")

if __name__ == "__main__":
    asyncio.run(main())
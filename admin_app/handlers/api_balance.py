"""
API Balance Handlers - Show balance for external services
"""
from aiohttp import web, ClientSession
import json
from admin_app.auth import check_admin_with_permission


async def get_openai_balance(api_key: str) -> dict:
    """Check OpenAI API key status (balance API is deprecated)"""
    if not api_key:
        return {'error': 'No API key configured'}

    try:
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        async with ClientSession() as session:
            # Test API key with models endpoint (lighter than billing)
            async with session.get('https://api.openai.com/v1/models', headers=headers) as resp:
                if resp.status == 200:
                    models = await resp.json()
                    model_count = len(models.get('data', []))
                    return {
                        'status': 'Active',
                        'models_available': model_count,
                        'info': 'API key is valid. Check usage at platform.openai.com',
                        'link': 'https://platform.openai.com/settings/organization/billing/overview'
                    }
                elif resp.status == 401:
                    return {'error': 'Invalid API key'}
                elif resp.status == 429:
                    return {'error': 'Rate limit exceeded'}
                else:
                    error_text = await resp.text()
                    return {'error': f'API error {resp.status}: {error_text[:100]}'}
    except Exception as e:
        return {'error': str(e)}


async def get_deepl_balance(api_key: str) -> dict:
    """Get DeepL usage statistics"""
    if not api_key:
        return {'error': 'No API key'}

    try:
        headers = {
            'Authorization': f'DeepL-Auth-Key {api_key}'
        }

        async with ClientSession() as session:
            async with session.get('https://api-free.deepl.com/v2/usage', headers=headers) as resp:
                if resp.status == 200:
                    usage = await resp.json()
                    character_count = usage.get('character_count', 0)
                    character_limit = usage.get('character_limit', 500000)
                    remaining = character_limit - character_count

                    return {
                        'used': character_count,
                        'limit': character_limit,
                        'remaining': remaining,
                        'unit': 'characters',
                        'percentage': round((character_count / character_limit) * 100, 2) if character_limit > 0 else 0
                    }
                else:
                    return {'error': f'API error: {resp.status}'}
    except Exception as e:
        return {'error': str(e)}


async def get_elevenlabs_balance(api_key: str) -> dict:
    """Get ElevenLabs subscription info"""
    if not api_key:
        return {'error': 'No API key'}

    try:
        headers = {
            'xi-api-key': api_key
        }

        async with ClientSession() as session:
            async with session.get('https://api.elevenlabs.io/v1/user/subscription', headers=headers) as resp:
                if resp.status == 200:
                    subscription = await resp.json()
                    character_count = subscription.get('character_count', 0)
                    character_limit = subscription.get('character_limit', 0)
                    remaining = character_limit - character_count

                    return {
                        'used': character_count,
                        'limit': character_limit,
                        'remaining': remaining,
                        'unit': 'characters',
                        'tier': subscription.get('tier', 'Unknown'),
                        'percentage': round((character_count / character_limit) * 100, 2) if character_limit > 0 else 0
                    }
                else:
                    return {'error': f'API error: {resp.status}'}
    except Exception as e:
        return {'error': str(e)}


async def get_yandex_balance(api_key: str) -> dict:
    """Get Yandex Cloud balance (if available)"""
    if not api_key:
        return {'error': 'No API key'}

    # Yandex doesn't provide public balance API for Translate
    # Return placeholder
    return {
        'info': 'Balance check not available via API',
        'link': 'https://console.cloud.yandex.com/billing'
    }


async def get_all_balances(request: web.Request) -> web.Response:
    """Get balances for all configured services"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'view_stats')

        from bot.database import db

        # Get API keys from database
        openai_key = await db.get_setting('openai_api_key', '')
        deepl_key = await db.get_setting('deepl_api_key', '')
        elevenlabs_key = await db.get_setting('elevenlabs_api_key', '')
        yandex_key = await db.get_setting('yandex_api_key', '')

        # Fetch balances concurrently
        import asyncio
        balances = await asyncio.gather(
            get_openai_balance(openai_key),
            get_deepl_balance(deepl_key),
            get_elevenlabs_balance(elevenlabs_key),
            get_yandex_balance(yandex_key),
            return_exceptions=True
        )

        return web.json_response({
            'success': True,
            'balances': {
                'openai': balances[0] if not isinstance(balances[0], Exception) else {'error': str(balances[0])},
                'deepl': balances[1] if not isinstance(balances[1], Exception) else {'error': str(balances[1])},
                'elevenlabs': balances[2] if not isinstance(balances[2], Exception) else {'error': str(balances[2])},
                'yandex': balances[3] if not isinstance(balances[3], Exception) else {'error': str(balances[3])}
            }
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch balances: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({'success': False, 'error': str(e)}, status=500)

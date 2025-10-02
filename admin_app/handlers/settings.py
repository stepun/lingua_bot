"""
System Settings Management Handlers
"""
from aiohttp import web
import json
from admin_app.auth import check_admin_with_permission


async def get_settings(request: web.Request) -> web.Response:
    """Get all system settings or filtered by category"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        from bot.database import db

        category = request.query.get('category')
        settings = await db.get_all_settings(category)

        # Group by category for UI
        grouped = {}
        for setting in settings:
            cat = setting['category']
            if cat not in grouped:
                grouped[cat] = []
            grouped[cat].append(setting)

        return web.json_response({
            'success': True,
            'settings': settings,
            'grouped': grouped
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to fetch settings: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def update_setting(request: web.Request) -> web.Response:
    """Update a single setting"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        from bot.database import db

        data = await request.json()
        key = data.get('key')
        value = data.get('value')
        category = data.get('category', 'general')
        description = data.get('description', '')

        if not key or value is None:
            raise web.HTTPBadRequest(reason="Missing key or value")

        success = await db.set_setting(key, value, category, description, admin_user_id)

        if success:
            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_user_id,
                action='update_setting',
                details=json.dumps({'key': key, 'value': str(value), 'category': category})
            )

        return web.json_response({
            'success': success,
            'message': 'Setting updated successfully'
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to update setting: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def delete_setting(request: web.Request) -> web.Response:
    """Delete setting (reset to .env default)"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        from bot.database import db

        key = request.match_info.get('key')
        if not key:
            raise web.HTTPBadRequest(reason="Missing key")

        success = await db.delete_setting(key)

        if success:
            await db.log_admin_action(
                admin_user_id=admin_user_id,
                action='delete_setting',
                details=json.dumps({'key': key})
            )

        return web.json_response({
            'success': success,
            'message': 'Setting deleted (reset to default)'
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to delete setting: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({'success': False, 'error': str(e)}, status=500)


async def bulk_update_settings(request: web.Request) -> web.Response:
    """Bulk update multiple settings at once"""
    try:
        admin_user_id, role, perms = await check_admin_with_permission(request, 'manage_settings')

        from bot.database import db

        data = await request.json()
        settings = data.get('settings', [])

        if not settings:
            raise web.HTTPBadRequest(reason="No settings provided")

        # Update all settings
        for setting in settings:
            await db.set_setting(
                key=setting['key'],
                value=setting['value'],
                category=setting.get('category', 'general'),
                description=setting.get('description', ''),
                updated_by=admin_user_id
            )

        # Log bulk update
        await db.log_admin_action(
            admin_user_id=admin_user_id,
            action='bulk_update_settings',
            details=json.dumps({'count': len(settings), 'keys': [s['key'] for s in settings]})
        )

        return web.json_response({
            'success': True,
            'message': f'Updated {len(settings)} settings'
        })

    except web.HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Failed to bulk update settings: {e}")
        import traceback
        traceback.print_exc()
        return web.json_response({'success': False, 'error': str(e)}, status=500)

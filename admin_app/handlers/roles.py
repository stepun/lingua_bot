"""Admin roles handlers for admin panel"""

from aiohttp import web
from admin_app.auth import check_admin_with_permission


async def get_admin_roles_endpoint(request):
    """Get all admin users with roles"""
    try:
        # Only admins can view roles
        user_id, role, permissions = await check_admin_with_permission(request, 'manage_roles')

        from bot.database import db

        # Get all admin users
        admins = await db.get_all_admin_users()

        return web.json_response({
            "admins": admins,
            "total": len(admins),
            "current_user": {
                "user_id": user_id,
                "role": role,
                "permissions": permissions
            }
        })
    except web.HTTPForbidden as e:
        return web.json_response({"error": str(e.text)}, status=403)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def assign_role_endpoint(request):
    """Assign role to admin user"""
    try:
        # Only admins can assign roles
        admin_id, admin_role, _ = await check_admin_with_permission(request, 'manage_roles')

        from bot.database import db

        # Get request data
        data = await request.json()
        target_user_id = data.get('user_id')
        new_role = data.get('role')
        custom_permissions = data.get('permissions')  # Optional custom permissions

        if not target_user_id or not new_role:
            return web.json_response({"error": "user_id and role are required"}, status=400)

        if new_role not in ['admin', 'moderator', 'analyst']:
            return web.json_response({"error": "Invalid role. Must be: admin, moderator, or analyst"}, status=400)

        # Prevent demoting yourself
        if target_user_id == admin_id and new_role != 'admin':
            return web.json_response({"error": "Cannot demote yourself"}, status=400)

        # Assign role
        success = await db.assign_role(target_user_id, new_role, custom_permissions)

        if success:
            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_id,
                action='assign_role',
                target_user_id=target_user_id,
                details={'role': new_role, 'permissions': custom_permissions}
            )

            return web.json_response({
                "success": True,
                "message": f"Role '{new_role}' assigned to user {target_user_id}"
            })
        else:
            return web.json_response({"error": "Failed to assign role"}, status=500)

    except web.HTTPForbidden as e:
        return web.json_response({"error": str(e.text)}, status=403)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def remove_role_endpoint(request):
    """Remove admin role from user"""
    try:
        # Only admins can remove roles
        admin_id, admin_role, _ = await check_admin_with_permission(request, 'manage_roles')

        from bot.database import db

        # Get target user ID from URL
        target_user_id = int(request.match_info['user_id'])

        # Prevent removing your own role
        if target_user_id == admin_id:
            return web.json_response({"error": "Cannot remove your own admin role"}, status=400)

        # Remove role
        success = await db.remove_admin_role(target_user_id)

        if success:
            # Log admin action
            await db.log_admin_action(
                admin_user_id=admin_id,
                action='remove_role',
                target_user_id=target_user_id,
                details={}
            )

            return web.json_response({
                "success": True,
                "message": f"Admin role removed from user {target_user_id}"
            })
        else:
            return web.json_response({"error": "Failed to remove role"}, status=500)

    except web.HTTPForbidden as e:
        return web.json_response({"error": str(e.text)}, status=403)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)


async def get_current_user_role_endpoint(request):
    """Get current user's role and permissions"""
    try:
        # Any admin can check their own role
        user_id, role, permissions = await check_admin_with_permission(request)

        return web.json_response({
            "user_id": user_id,
            "role": role,
            "permissions": permissions
        })
    except web.HTTPForbidden as e:
        return web.json_response({"error": str(e.text)}, status=403)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return web.json_response({"error": str(e)}, status=500)

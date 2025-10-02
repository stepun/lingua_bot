"""Telegram WebApp authentication"""

import hmac
import hashlib
import json
from urllib.parse import parse_qs
from typing import Optional, Dict, Tuple
from config import config

# Role-based permissions mapping
ROLE_PERMISSIONS = {
    'admin': ['*'],  # Full access (includes manage_roles, grant_premium, etc.)
    'moderator': ['view_dashboard', 'view_users', 'view_logs', 'view_feedback', 'view_admin_logs',
                  'block_user', 'send_message', 'view_history', 'update_feedback'],
    'analyst': ['view_dashboard', 'view_stats']
}


def validate_telegram_webapp_data(init_data: str) -> Optional[Dict[str, str]]:
    """
    Validate Telegram WebApp init data

    Args:
        init_data: Raw init data string from Telegram WebApp

    Returns:
        Parsed data dict if valid, None otherwise
    """
    try:
        # Parse the init data
        parsed = parse_qs(init_data)

        # Extract hash
        received_hash = parsed.get('hash', [None])[0]
        if not received_hash:
            return None

        # Remove hash from data
        data_check_string_parts = []
        for key in sorted(parsed.keys()):
            if key != 'hash':
                value = parsed[key][0]
                data_check_string_parts.append(f"{key}={value}")

        data_check_string = '\n'.join(data_check_string_parts)

        # Create secret key
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=config.BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Verify hash
        if calculated_hash != received_hash:
            return None

        # Return parsed data
        result = {}
        for key, value in parsed.items():
            if key != 'hash':
                result[key] = value[0]

        return result

    except Exception as e:
        print(f"Error validating Telegram WebApp data: {e}")
        return None


def is_admin(user_id: int) -> bool:
    """Check if user is admin (legacy - checks ADMIN_IDS only)"""
    return user_id in config.ADMIN_IDS


async def get_user_role_and_permissions(user_id: int) -> Tuple[str, list]:
    """Get user role and permissions from database

    Returns:
        Tuple[str, list]: (role, permissions list)
    """
    from bot.database import db

    # Check if user has role in database
    role_data = await db.get_user_role(user_id)

    if role_data:
        role = role_data['role']
        # Get permissions from role mapping
        permissions = ROLE_PERMISSIONS.get(role, [])
        # Merge with custom permissions from database if any
        custom_perms = role_data.get('permissions', {})
        if custom_perms and isinstance(custom_perms, dict):
            custom_perms_list = custom_perms.get('additional', [])
            permissions = list(set(permissions + custom_perms_list))
        return role, permissions

    # Fallback: check legacy ADMIN_IDS
    if is_admin(user_id):
        return 'admin', ['*']

    return None, []


def has_permission(permissions: list, required_permission: str) -> bool:
    """Check if user has required permission

    Args:
        permissions: List of user permissions
        required_permission: Permission to check (e.g., 'view_users', 'block_user')

    Returns:
        bool: True if user has permission
    """
    if '*' in permissions:  # Admin has all permissions
        return True
    return required_permission in permissions


def check_admin(request):
    """Check if request is from admin using Telegram WebApp authentication (legacy compatibility)

    Returns:
        int: Admin user ID if valid

    Raises:
        web.HTTPForbidden: If authentication fails

    Note: This function only checks basic admin access. For permission-based access,
          use check_admin_with_permission() instead.
    """
    from aiohttp import web

    # Get Telegram init data from header
    init_data = request.headers.get('X-Telegram-Init-Data')

    if not init_data:
        raise web.HTTPForbidden(text="Access denied: Telegram authentication required")

    # Validate Telegram data
    validated_data = validate_telegram_webapp_data(init_data)

    if not validated_data:
        raise web.HTTPForbidden(text="Access denied: Invalid Telegram data")

    # Extract user data
    try:
        user_json = validated_data.get('user', '{}')
        user_data = json.loads(user_json)
        user_id = user_data.get('id')
    except (json.JSONDecodeError, AttributeError):
        raise web.HTTPForbidden(text="Access denied: Invalid user data")

    if not user_id:
        raise web.HTTPForbidden(text="Access denied: user_id not found")

    if not is_admin(user_id):
        raise web.HTTPForbidden(text=f"Access denied: user {user_id} is not admin")

    return user_id


async def check_admin_with_permission(request, required_permission: str = None):
    """Check if request is from admin with specific permission

    Args:
        request: aiohttp request object
        required_permission: Optional permission to check (e.g., 'view_users', 'block_user')
                           If None, only checks basic admin access

    Returns:
        Tuple[int, str, list]: (user_id, role, permissions)

    Raises:
        web.HTTPForbidden: If authentication or authorization fails
    """
    from aiohttp import web

    # Get Telegram init data from header
    init_data = request.headers.get('X-Telegram-Init-Data')

    if not init_data:
        raise web.HTTPForbidden(text="Access denied: Telegram authentication required")

    # Validate Telegram data
    validated_data = validate_telegram_webapp_data(init_data)

    if not validated_data:
        raise web.HTTPForbidden(text="Access denied: Invalid Telegram data")

    # Extract user data
    try:
        user_json = validated_data.get('user', '{}')
        user_data = json.loads(user_json)
        user_id = user_data.get('id')
    except (json.JSONDecodeError, AttributeError):
        raise web.HTTPForbidden(text="Access denied: Invalid user data")

    if not user_id:
        raise web.HTTPForbidden(text="Access denied: user_id not found")

    # Get user role and permissions
    role, permissions = await get_user_role_and_permissions(user_id)

    if not role:
        raise web.HTTPForbidden(text=f"Access denied: user {user_id} has no admin role")

    # Check specific permission if required
    if required_permission and not has_permission(permissions, required_permission):
        raise web.HTTPForbidden(text=f"Access denied: insufficient permissions (required: {required_permission})")

    return user_id, role, permissions

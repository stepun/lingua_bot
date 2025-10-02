"""Admin panel handlers"""

from .stats import get_stats, get_daily_stats, get_language_stats, get_performance_stats
from .users import (
    get_users,
    block_user_endpoint,
    unblock_user_endpoint,
    grant_premium_endpoint,
    send_message_endpoint,
    get_user_history
)
from .logs import get_translation_logs
from .feedback import get_feedback, update_feedback_status
from .admin_logs import get_admin_logs_endpoint
from .roles import (
    get_admin_roles_endpoint,
    assign_role_endpoint,
    remove_role_endpoint,
    get_current_user_role_endpoint
)
from .settings import (
    get_settings,
    update_setting,
    delete_setting,
    bulk_update_settings
)

__all__ = [
    'get_stats',
    'get_daily_stats',
    'get_language_stats',
    'get_performance_stats',
    'get_users',
    'block_user_endpoint',
    'unblock_user_endpoint',
    'grant_premium_endpoint',
    'send_message_endpoint',
    'get_user_history',
    'get_translation_logs',
    'get_feedback',
    'update_feedback_status',
    'get_admin_logs_endpoint',
    'get_admin_roles_endpoint',
    'assign_role_endpoint',
    'remove_role_endpoint',
    'get_current_user_role_endpoint',
    'get_settings',
    'update_setting',
    'delete_setting',
    'bulk_update_settings'
]

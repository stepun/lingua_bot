"""Telegram WebApp authentication"""

import hmac
import hashlib
from urllib.parse import parse_qs
from typing import Optional, Dict
from config import config


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
    """Check if user is admin"""
    return user_id in config.ADMIN_IDS

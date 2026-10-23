import secrets
from datetime import datetime, timedelta, timezone

from .cipher import cipher
from typing import TypedDict

#return type for create_api_key function
class CreateApiKeyResponse(TypedDict):
    api_key: str
    api_secret: str
    encrypted_secret: str
    expires_at: datetime

def generate_api_key(expires_in_days: int = 30) -> CreateApiKeyResponse:
    """
    Generate a new API key for a user.

    Args:
        expires_in_days (int): The number of days until the API key expires. Default is 30 days.
        """

    api_key = secrets.token_hex(16)

    api_secret = secrets.token_urlsafe(32)

    encrypted_secret = cipher.encrypt(api_secret.encode("utf-8")).decode("ascii")

    expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

    return {
        "api_key": api_key,
        "api_secret": api_secret,
        "encrypted_secret": encrypted_secret,
        "expires_at": expires_at,
    }
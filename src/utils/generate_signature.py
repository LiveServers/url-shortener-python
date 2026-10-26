import base64
from datetime import datetime, timezone
import hashlib
import hmac

from beanie import PydanticObjectId

"""
This module provides a utility function to generate an API signature for a given API key and user ID. 
The signature is generated using HMAC with SHA-256 hashing and includes a timestamp, user ID"""
def generate_signature(api_key: str, user_id: PydanticObjectId) -> tuple[str, str]:
    """
    Generate a new API signature.

    Returns:
        str: A new API signature.
    """
    timestamp = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

    hmac_new = hmac.new(api_key.encode("utf-8"), digestmod=hashlib.sha256)
    hmac_new.update(timestamp.encode("utf-8"))
    hmac_new.update(str(user_id).encode("utf-8"))
    hmac_new.update("sid_request".encode("utf-8"))

    signature = base64.b64encode(hmac_new.digest()).decode("utf-8")
    return signature, timestamp

def verify_signature(api_key: str, user_id: PydanticObjectId, signature: str, timestamp: str) -> bool:
    """
    Verify the provided API signature.

    Args:
        api_key (str): The API key used to generate the signature.
        user_id (PydanticObjectId): The user ID associated with the signature.
        signature (str): The signature to verify.
        timestamp (str): The timestamp used in the signature generation.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    hmac_new = hmac.new(api_key.encode("utf-8"), digestmod=hashlib.sha256)
    hmac_new.update(timestamp.encode("utf-8"))
    hmac_new.update(str(user_id).encode("utf-8"))
    hmac_new.update("sid_request".encode("utf-8"))

    expected_signature = base64.b64encode(hmac_new.digest()).decode("utf-8")
    return hmac.compare_digest(expected_signature, signature)
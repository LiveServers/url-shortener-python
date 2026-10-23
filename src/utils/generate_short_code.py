import secrets
import string

BASE62_ALPHABET = string.ascii_lowercase + string.digits + string.ascii_uppercase

def generate_short_code(length: int = 10) -> str:
    """
    Generate a random short code of the specified length.

    Args:
        length (int): The length of the short code to generate. Default is 10.

    Returns:
        str: A randomly generated short code.
    """
    return "".join(secrets.choice(BASE62_ALPHABET) for _ in range(length))
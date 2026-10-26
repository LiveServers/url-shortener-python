from cryptography.fernet import Fernet

from src.config import settings

cipher = Fernet(settings.api_secret_encryption_key.encode("ascii"))
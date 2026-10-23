import os

from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

secret = str(os.getenv("API_SECRET_ENCRYPTION_KEY"))

cipher = Fernet(secret.encode("ascii"))
""" For this user model, I am looking for it to log in/out, but rather just have an API Key,
    Signature that we can validate and rate limit.
"""

from datetime import datetime, timezone
from typing import Annotated
from pydantic import Field, EmailStr
from beanie import Document, Indexed


class User(Document):
    email: Annotated[EmailStr, Indexed(unique=True)] = Field(..., description="The user's email address.")
    bucket_size: int = Field(100, ge=1, description="The maximum number of requests allowed in the rate limit bucket.")
    refill_rate: float = Field(2.0, gt=0.1, description="The rate at which the bucket refills (requests per second).")
    created_at:datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "users"
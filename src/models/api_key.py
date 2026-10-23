from datetime import datetime, timezone
from typing import Annotated, Optional

from beanie import Document, Indexed, PydanticObjectId, PydanticObjectId
from pydantic import Field


class APIKey(Document):
    api_key: Annotated[str, Indexed(unique=True)] = Field(..., description="The unique API key for authentication.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    user_id: Annotated[PydanticObjectId, Indexed()] = Field(..., description="The ID of the user associated with this API key.")
    encrypted_secret: str = Field(..., description="The encrypted secret associated with the API key.")
    enabled: bool = Field(default=True, description="Indicates whether the API key is enabled or disabled.")

    class Settings:
        name = "api_keys"
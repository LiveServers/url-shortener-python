from datetime import datetime, timezone
from typing import Annotated

from beanie import Document, Indexed, PydanticObjectId
from pydantic import Field

class URL(Document):
    original_url: str = Field(..., description="The original long URL to be shortened.")
    short_url: Annotated[str, Indexed(unique=True)] = Field(..., description="The generated short URL.")
    created_at:datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Annotated[PydanticObjectId, Indexed()] = Field(..., description="The ID of the user who created this short URL.")

    class Settings:
        name = "urls"
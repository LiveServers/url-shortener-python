from beanie import PydanticObjectId
from pydantic import HttpUrl
from pymongo.errors import DuplicateKeyError

from src.models.url_shortener import URL
from src.utils.generate_short_code import generate_short_code

MAX_ATTEMPTS = 5  # Maximum number of allowed attempts

async def create_short_link(
    original_url: HttpUrl,
    user_id: PydanticObjectId,
) -> URL:
    for _ in range(MAX_ATTEMPTS):
        link = URL(
            original_url=str(original_url),
            short_url=generate_short_code(),
            created_by=user_id,
        )

        try:
            await link.insert()
            return link

        except DuplicateKeyError as exc:
            # Retry only a short-code collision.
            # Other unique-index violations should surface normally.
            key_pattern = (exc.details or {}).get("keyPattern", {})

            if key_pattern != {"short_code": 1}:
                raise

    raise RuntimeError("Could not allocate a unique short code")
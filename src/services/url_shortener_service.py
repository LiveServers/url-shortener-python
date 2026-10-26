from fastapi import HTTPException, Request
from pydantic import HttpUrl

from src.models.api_key import APIKey
from src.models.url_shortener import URL
from src.models.user import User
from src.services.create_short_link import create_short_link
from src.services.rate_limiter import RateLimiter
from src.utils.generate_signature import verify_signature


async def get_validated_user_for_api_key(api_key: str) -> User:
    api_key_record = await APIKey.find_one(APIKey.api_key == api_key)
    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid API key")

    current_user = await User.find_one(User.id == api_key_record.user_id)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid user")

    return current_user


async def validate_rate_limit(request: Request, user: User) -> None:
    user_id = user.id
    if user_id is None:
        raise HTTPException(status_code=500, detail="Error occurred")

    rate_limiter: RateLimiter = request.app.state.rate_limiter
    allowed, _, retry_after = await rate_limiter.is_allowed(
        user_id=str(user_id),
        capacity=user.bucket_size,
        refill_rate=user.refill_rate,
    )

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )


async def shorten_url_for_user(
    api_key: str,
    user: User,
    signature: str,
    timestamp: str,
    original_url: HttpUrl,
) -> URL:
    user_id = user.id
    if user_id is None:
        raise HTTPException(status_code=500, detail="Error occurred")
    
    if not verify_signature(api_key, user_id, signature, timestamp):
        raise HTTPException(status_code=401, detail="Invalid signature")

    return await create_short_link(original_url, user_id)

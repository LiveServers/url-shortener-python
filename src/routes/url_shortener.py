from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import HttpUrl
from src.models.api_key import APIKey
from src.models.url_shortener import URL
from src.models.user import User
from src.services.create_short_link import create_short_link
from src.services.rate_limiter import RateLimiter
from src.utils.generate_signature import verify_signature

router = APIRouter(
    prefix="/rate_limit/v1",
    tags=["rate_limit"],
    responses={404: {"description": "Not found"}},
)

MAX_ATTEMPTS = 5  # Maximum number of allowed attempts

@router.post("/shorten_url",response_model=URL, status_code=201)
async def shorten_url(
    request: Request, 
    api_key: Annotated[str, Header(alias="X-API-Key")],
    timestamp: Annotated[str, Header(alias="X-Timestamp")],
    signature: Annotated[str, Header(alias="X-Signature")],
    original_url: HttpUrl,
    ):
    """
    Endpoint to shorten a URL with rate limiting.

    Args:
        request (Request): The incoming request object.
        response (Response): The outgoing response object.

    Returns:
        URL: The shortened URL object if the request is allowed, otherwise raises an HTTPException.
    """
    try:
        api_key_record = await APIKey.find_one(APIKey.api_key == api_key)
        if not api_key_record:
            raise HTTPException(status_code=401, detail="Invalid API key")

        current_user = await User.find_one(User.id == api_key_record.user_id)
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid user")

        user_id = current_user.id
        if user_id is None:
            raise HTTPException(status_code=500, detail="Error occurred")

        rate_limiter: RateLimiter = request.app.state.rate_limiter
        allowed, remaining, retry_after = await rate_limiter.is_allowed(
            user_id=str(user_id),
            capacity=current_user.bucket_size,
            refill_rate=current_user.refill_rate,
        )

        if not allowed:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
                headers={"Retry-After": str(retry_after)},
            )

        # validate signature
        if not verify_signature(api_key, user_id, signature, timestamp):
            raise HTTPException(status_code=401, detail="Invalid signature")

        # If allowed, proceed to shorten the URL
        link = await create_short_link(original_url, user_id)
        return link

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import RedirectResponse
from pydantic import HttpUrl

from src.models.url_shortener import URL
from src.services.url_shortener_service import (
    get_validated_user_for_api_key,
    shorten_url_for_user,
    validate_rate_limit,
)

router = APIRouter(
    prefix="/url_shortener/v1",
    tags=["url_shortener"],
    responses={404: {"description": "Not found"}},
)

@router.post("/shorten", response_model=URL, status_code=201)
async def shorten_url(
    request: Request,
    api_key: Annotated[str, Header(alias="X-API-Key")],
    timestamp: Annotated[str, Header(alias="X-Timestamp")],
    signature: Annotated[str, Header(alias="X-Signature")],
    original_url: HttpUrl,
):
    try:
        current_user = await get_validated_user_for_api_key(api_key)
        await validate_rate_limit(request, current_user)
        return await shorten_url_for_user(
            api_key=api_key,
            user=current_user,
            signature=signature,
            timestamp=timestamp,
            original_url=original_url,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc

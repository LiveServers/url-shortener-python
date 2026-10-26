from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse

from src.models.url_shortener import URL

router = APIRouter(tags=["Redirects"])


@router.get("/{short_url}")
async def redirect_short_url(request: Request, short_url: str):
    redis = request.app.state.redis
    
    cache_key = f"short_url:{short_url}"
    original_url = await redis.get(cache_key)

    if not original_url:
        link = await URL.find_one(URL.short_url == short_url)

        if link is None:
            raise HTTPException(
                status_code=404,
                detail="Short URL not found",
            )
        original_url = link.original_url
        await redis.set(cache_key, original_url, ex=3600)

    return RedirectResponse(
        url=original_url,
        status_code=302,
    )
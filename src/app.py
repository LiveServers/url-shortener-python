from contextlib import asynccontextmanager

from fastapi import FastAPI
from beanie import init_beanie
from pymongo import AsyncMongoClient
from redis.asyncio import Redis
from starlette.middleware.cors import CORSMiddleware

from src.config import settings
from src.models.user import User
from src.models.url_shortener import URL
from src.models.api_key import APIKey
from src.services.rate_limiter import RateLimiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncMongoClient(settings.mongodb_uri)
    redis_client = Redis.from_url(settings.redis_url, decode_responses=True)

    try:
        await init_beanie(
            database=client.get_default_database(),
            document_models=[User, URL, APIKey],
        )
        await redis_client.ping()  # Check if Redis is reachable

        app.state.mongo_client = client
        app.state.redis = redis_client
        app.state.rate_limiter = RateLimiter(redis_client)

        yield
    finally:
        try:
            await client.close()
        finally:
            await redis_client.aclose()

DESCRIPTION = """
URL_Shortener API is a simple and efficient service that allows users to shorten long URLs into compact, easy-to-share links. 
With this API, you can create short links, manage them, and track their usage. 
It is designed for developers who want to integrate URL shortening functionality into their applications or services.
"""

app = FastAPI(
    title="URL_Shortener",
    description=DESCRIPTION,
    version="0.1.0",
    # contact={
    #     "name": "Hello World Jr",
    #     "url": "https://myserver.dev",
    #     "email": "helloworld@myserver.dev",
    # },
    # license_info={
    #     "name": "MIT",
    #     "url": "https://github.com/flyinactor91/fastapi-beanie-jwt/blob/main/LICENSE",
    # },
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
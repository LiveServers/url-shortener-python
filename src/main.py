
from .app import app
from .routes import health, users, api_key, url_shortener, url_redirect

app.include_router(health.router)
app.include_router(users.router)
app.include_router(api_key.router)
app.include_router(url_shortener.router)
app.include_router(url_redirect.router)
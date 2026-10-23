# URL Shortener API

A FastAPI-based URL shortening service built with MongoDB for persistence, Redis for rate limiting, and Docker Compose for local orchestration. The project is designed to let users create accounts, generate API keys, and shorten URLs through signed API requests.

## Features

- Create and store users in MongoDB
- Generate API keys for authenticated clients
- Validate HMAC-based request signatures
- Enforce Redis-backed token-bucket rate limiting per user
- Store shortened URLs with metadata including the creating user
- Run the full stack locally with Docker Compose
- Explore the API interactively with Swagger UI

## Tech Stack

- Python 3.13
- FastAPI
- Beanie + PyMongo for MongoDB models
- Redis for rate limiting
- Docker / Docker Compose
- Pydantic for validation
- Fernet encryption for API secret storage

## Project Structure

```text
.
├── docker-compose.yml
├── .env.example
├── LOCAL.md
├── README.md
├── requirements.txt
├── src/
│   ├── app.py
│   ├── main.py
│   ├── Dockerfile
│   ├── models/
│   │   ├── api_key.py
│   │   ├── url_shortener.py
│   │   └── user.py
│   ├── routes/
│   │   ├── api_key.py
│   │   ├── health.py
│   │   ├── url_shortener.py
│   │   └── users.py
│   ├── services/
│   │   ├── create_short_link.py
│   │   └── rate_limiter.py
│   └── utils/
│       ├── api_key.py
│       ├── cipher.py
│       ├── generate_short_code.py
│       └── generate_signature.py
└──
```

## Runtime Architecture

The application starts with a FastAPI app and initializes MongoDB and Redis during the app lifespan. The backend connects to MongoDB and Redis at startup, registers Beanie document models, and initializes the user-specific rate limiter.

Services exposed by Docker Compose:

- API backend: http://127.0.0.1:3100
- MongoDB: http://127.0.0.1:27017
- Mongo Express: http://127.0.0.1:8081
- Redis: http://127.0.0.1:6379
- RedisInsight: http://127.0.0.1:5540

## Prerequisites

Before you start, make sure you have:

- Docker and Docker Compose installed
- Python 3.13 (if running outside Docker)
- Access to a local environment capable of exposing ports 3100, 27017, 6379, 8081, and 5540

## Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Then fill in the required values in `.env`:

```env
MONGODB_INITDB_ROOT_USERNAME=your_mongo_user
MONGODB_INITDB_ROOT_PASSWORD=your_mongo_password
API_SECRET_ENCRYPTION_KEY=your_fernet_key
MONGODB_URI=mongodb://your_mongo_user:your_mongo_password@mongodb:27017/?authSource=admin
REDIS_URL=
MONGO_UI_USERNAME=
MONGO_UI_PASSWORD=
```

### Generate the encryption key

This app uses Fernet encryption for stored API secrets. Generate a valid key with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Paste the output into `API_SECRET_ENCRYPTION_KEY`.

## Running the Project

### Option 1: Docker Compose (recommended)

```bash
docker compose up -d --build
```

Then confirm the backend health endpoint responds:

```bash
curl http://127.0.0.1:3100/health/v1/check
```

Expected result:

```json
{"status":"healthy"}
```

### Option 2: Local development without Docker

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 3100
```

The app will be available at:

- http://127.0.0.1:3100
- http://127.0.0.1:3100/docs for Swagger UI
- http://127.0.0.1:3100/redoc for ReDoc

## API Overview

The application exposes the following routes.

| Endpoint | Method | Description |
|---|---|---|
| `/health/v1/check` | GET | Basic app health check |
| `/health/v1/database` | GET | Verifies MongoDB connectivity |
| `/users/v1/create` | POST | Creates a new user |
| `/users/v1/retrieve-users` | GET | Lists all users |
| `/api_keys/v1/create` | POST | Generates an API key for a user |
| `/rate_limit/v1/shorten_url` | POST | Shortens a URL using API-key authentication and a request signature |

## Authentication Model

This project does not use standard session-based auth. Instead, it relies on:

- an API key generated for a user
- a timestamp header
- a signature header
- Redis-based per-user rate limiting

The request signature is generated with HMAC-SHA256 using the API key as the secret, and the app verifies it on the server before shortening a URL.

## Example Usage

### 1. Create a user

```bash
curl -X POST "http://127.0.0.1:3100/users/v1/create" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "bucket_size": 100,
    "refill_rate": 2.0
  }'
```

### 2. Create an API key for a user

```bash
curl -X POST "http://127.0.0.1:3100/api_keys/v1/create?userid=<USER_ID>"
```

### 3. Shorten a URL

```bash
curl -X POST "http://127.0.0.1:3100/rate_limit/v1/shorten_url?original_url=https://example.com/very/long/path" \
  -H "X-API-Key: <api_key>" \
  -H "X-Timestamp: <timestamp>" \
  -H "X-Signature: <signature>"
```

## Rate Limiting

The service uses a token-bucket limiter in Redis. Each user has a configurable:

- `bucket_size`: maximum bucket capacity
- `refill_rate`: rate of token refill per second

If the user exceeds the available request budget, the API responds with:

- HTTP `429 Too Many Requests`
- a `Retry-After` header with the suggested delay

## Notes

- The current app uses wildcard CORS settings for local development.
- The backend exposes a minimal API and is ideal as a starting point for a production-grade URL shortener.
- The project is intentionally lightweight and service-oriented, with logic split across routes, services, and models.

## Useful Commands

```bash
docker compose logs -f backend
docker compose down
```

## License

This project does not currently include a license file. Add one if you plan to distribute or publish the project publicly.

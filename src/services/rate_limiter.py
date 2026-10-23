import math

from redis.asyncio import Redis


TOKEN_BUCKET_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])

-- Use Redis's clock for all backend instances.
local clock = redis.call('TIME')
local now = tonumber(clock[1]) + tonumber(clock[2]) / 1000000

local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
local tokens = tonumber(bucket[1])
local last_refill = tonumber(bucket[2])

if tokens == nil or last_refill == nil then
    tokens = capacity
    last_refill = now
end

-- Avoid negative elapsed time if the clock moves backward.
now = math.max(now, last_refill)
local elapsed = now - last_refill

tokens = math.min(capacity, tokens + elapsed * refill_rate)

local allowed = 0
local retry_after = 0

if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
else
    retry_after = math.ceil((1 - tokens) / refill_rate)
end

redis.call(
    'HSET', key,
    'tokens', tokens,
    'last_refill', now
)

-- After this much inactivity, the bucket would be full anyway.
local ttl = math.ceil(capacity / refill_rate) + 1
redis.call('EXPIRE', key, ttl)

return {allowed, tostring(tokens), retry_after}
"""


class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.script = redis_client.register_script(
            TOKEN_BUCKET_SCRIPT
        )

    async def is_allowed(
        self,
        user_id: str,
        capacity: int,
        refill_rate: float,
    ) -> tuple[bool, float, int]:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")

        if not math.isfinite(refill_rate) or refill_rate <= 0:
            raise ValueError("refill_rate must be finite and positive")

        result = await self.script(
            keys=[f"rate_limit:user:{user_id}"],
            args=[capacity, refill_rate],
        )

        allowed, remaining_tokens, retry_after = result

        return (
            bool(allowed),
            float(remaining_tokens),
            int(retry_after),
        )
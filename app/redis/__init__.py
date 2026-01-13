from redis import Redis
import os

red = Redis(
        host=str(os.getenv("REDIS_HOST", "127.0.0.1")),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True
        )

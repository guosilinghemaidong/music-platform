import redis
from app.config import REDIS_HOST, REDIS_PORT, REDIS_DB

# 创建 Redis 连接
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    protocol=2  # ← 加这一行，使用 RESP2 协议兼容 Redis 5.0
)

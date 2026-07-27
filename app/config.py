import os

# 数据库连接地址
# Docker 环境下通过环境变量传入，本地开发用默认值
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "mysql+aiomysql://root:ztsmysql@localhost:3306/music_platform?charset=utf8mb4"
)

# JWT 配置
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-change-later")
ALGORITHM = "HS256"

# Redis 配置
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_DB = int(os.environ.get("REDIS_DB", 0))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import DATABASE_URL

# 创建异步数据库引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=True,          # 是否输出 SQL 日志
    pool_size=10,       # 连接池保持的连接数
    max_overflow=20,    # 超出 pool_size 后最多再创建多少个
)

# 创建异步会话工厂（用来生成操作数据库的 session 对象）
AsyncSessionLocal = async_sessionmaker(
    bind=engine,           # 绑定引擎
    class_=AsyncSession,   # 指定使用异步 Session
    expire_on_commit=False # 提交后不过期（避免提交后自动重新查询）
)

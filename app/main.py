from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user
from app.routers import music
from app.routers import singer
from app.routers import album
from app.routers import category
from app.routers import collection
from app.routers import music_like
from app.routers import follow
from app.routers import comment
from fastapi.staticfiles import StaticFiles
from app.routers import upload
from app.routers import post
from app.routers import admin
from app.routers import search
from app.redis import redis_client
from contextlib import asynccontextmanager
from app.models.base import Base
from app.database import engine

# 导入所有模型（让 SQLAlchemy 知道有哪些表要建）
from app.models import user as user_models, music as music_models, singer as singer_models
from app.models import album as album_models, category as category_models
from app.models import collection as collection_models, music_like as music_like_models
from app.models import follow as follow_models, comment as comment_models
from app.models import post as post_models, post_like as post_like_models
from app.models import post_comment as post_comment_models
from app.models import play_history as play_history_models
from app.models import playlist as playlist_models, playlist_music as playlist_music_models
from app.routers import playlist

@asynccontextmanager
async def lifespan(app):
    # 启动时：自动创建所有数据库表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # 应用运行中

app = FastAPI(title="音乐社交平台", lifespan=lifespan)


# 允许跨域（前端 localhost:5173 访问后端 localhost:8000）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 本地开发（npm run dev）
        "http://localhost",  # Docker 部署（Nginx 80 端口）
    ],
    allow_credentials=True,
    allow_methods=["*"],    # 允许所有请求方法
    allow_headers=["*"],    # 允许所有请求头
)

app.include_router(user.router)
app.include_router(music.router)
app.include_router(singer.router)
app.include_router(album.router)
app.include_router(category.router)
app.include_router(collection.router)
app.include_router(music_like.router)
app.include_router(follow.router)
app.include_router(comment.router)
app.include_router(post.router)
app.include_router(admin.router)
app.include_router(search.router)
app.include_router(playlist.router)



@app.get("/")
async def root():
    return {"message": "音乐社交平台 API 运行中！"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# 注册上传路由
app.include_router(upload.router)

# 挂载静态文件目录（让上传的文件可以通过 URL 访问）
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/test-redis")
async def test_redis():
    # 写入
    redis_client.set("test_key", "hello redis")
    # 读取
    value = redis_client.get("test_key")
    return {"message": value}
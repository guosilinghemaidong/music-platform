from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user
from app.routers import music


app = FastAPI(title="音乐社交平台", description="FastAPI + Vue3 全栈项目")

# 允许跨域（前端 localhost:5173 访问后端 localhost:8000）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 允许前端地址
    allow_credentials=True,
    allow_methods=["*"],    # 允许所有请求方法
    allow_headers=["*"],    # 允许所有请求头
)

app.include_router(user.router)
app.include_router(music.router)

@app.get("/")
async def root():
    return {"message": "音乐社交平台 API 运行中！"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

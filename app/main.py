from fastapi import FastAPI
from app.routers import user  # 导入用户路由

app = FastAPI(title="音乐社交平台", description="FastAPI + Vue3 全栈项目")

# 注册路由（把 user.router 里的所有接口都加进来）
app.include_router(user.router)


@app.get("/")
async def root():
    return {"message": "音乐社交平台 API 运行中！"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}

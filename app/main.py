from fastapi import FastAPI

# 创建 FastAPI 应用实例
app = FastAPI(title="音乐社交平台", description="FastAPI + Vue3 全栈项目")


# 根路径接口，用来测试项目是否正常运行
@app.get("/")
async def root():
    return {"message": "音乐社交平台 API 运行中！"}


# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok"}

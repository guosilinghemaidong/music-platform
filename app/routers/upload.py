# 导入
from fastapi import UploadFile, File
import os
import time
from fastapi import APIRouter



router = APIRouter(prefix="/upload", tags=["上传"])




@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    # 生成唯一文件名
    filename = f"{int(time.time())}_{file.filename}"
    #保存到images目录
    save_path = os.path.join("static", "images", filename)
    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
    #返回文件访问路径
    return {"filename": f"/static/images/{filename}"}




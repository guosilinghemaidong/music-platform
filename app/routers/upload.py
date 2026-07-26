# 导入
from fastapi import UploadFile, File, HTTPException
import os
import time
from fastapi import APIRouter



router = APIRouter(prefix="/upload", tags=["上传"])


# 允许的文件类型白名单
ALLOWED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_MUSIC_TYPES = {".mp3", ".wav", ".flac", ".aac", ".ogg"}
ALLOWED_LYRIC_TYPES = {".txt", ".lrc"}


@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    # 检查文件扩展名是否合法
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式：{ext}，仅支持 {', '.join(ALLOWED_IMAGE_TYPES)}")

    # 生成唯一文件名
    filename = f"{int(time.time())}_{file.filename}"
    # 保存到 images 目录
    save_path = os.path.join("static", "images", filename)
    # 确保目录存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
    # 返回文件访问路径
    return {"filename": f"/static/images/{filename}"}


@router.post("/music")
async def upload_music(file: UploadFile = File(...)):
    # 检查文件扩展名是否合法（只允许音频格式）
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_MUSIC_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的音频格式：{ext}，仅支持 {', '.join(ALLOWED_MUSIC_TYPES)}")

    # 生成唯一文件名
    filename = f"{int(time.time())}_{file.filename}"
    # 保存到 music 目录
    save_path = os.path.join("static", "music", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": f"/static/music/{filename}"}


@router.post("/lyric")
async def upload_lyric(file: UploadFile = File(...)):
    # 检查文件扩展名是否合法（只允许歌词文件）
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_LYRIC_TYPES:
        raise HTTPException(status_code=400, detail=f"不支持的歌词格式：{ext}，仅支持 {', '.join(ALLOWED_LYRIC_TYPES)}")

    # 生成唯一文件名
    filename = f"{int(time.time())}_{file.filename}"
    # 保存到 lyric 目录
    save_path = os.path.join("static", "lyric", filename)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": f"/static/lyric/{filename}"}

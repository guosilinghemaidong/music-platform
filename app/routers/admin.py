from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.routers.user import get_database

from app.models.user import User
from app.models.music import Music
from app.routers.user import get_current_admin
from app.schemas.admin import (
    AdminUserResponse, AdminUserListResponse, UserStatusUpdate, UserStatusResponse,
    AdminMusicResponse, AdminMusicListResponse, MusicAuditUpdate, MusicAuditResponse
)


router = APIRouter(prefix="/admin", tags=["管理员"])



# ==================== 用户管理 ====================

@router.get("/users", response_model=AdminUserListResponse)
async def get_user_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_database)
):
    # 1. 计算跳过多少条（和 singer/list 一样的分页逻辑）
    offset = (page - 1) * page_size

    # 2. 查询用户总数（SELECT COUNT(*) FROM user）
    total_result = await db.execute(select(User))
    total = len(total_result.scalars().all())

    # 3. 查询当前页的用户数据（SELECT * FROM user LIMIT page_size OFFSET offset）
    result = await db.execute(
        select(User)
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()

    # 4. 返回分页结果
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.put("/user/{user_id}/status", response_model=UserStatusResponse)
async def update_user_status(
    user_id: int,                              # 要修改的用户ID
    data: UserStatusUpdate,                    # 请求体：目标状态
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_database)
):
    # 1. 查找目标用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    # 2. 用户不存在
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 3. 检查状态值是否合法（只允许 0 或 1）
    if data.status not in [0, 1]:
        raise HTTPException(status_code=400, detail="状态值无效，必须是 0 或 1")

    # 4. 更新用户状态
    user.status = data.status
    await db.flush()

    return user


# ==================== 音乐审核 ====================

@router.get("/music/list", response_model=AdminMusicListResponse)
async def get_pending_music_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_database)
):
    # 1. 计算跳过多少条
    offset = (page - 1) * page_size

    # 2. 查询待审核音乐总数（status=0 表示下架/待审核）
    total_result = await db.execute(
        select(Music).where(Music.status == 0)
    )
    total = len(total_result.scalars().all())

    # 3. 查询当前页的待审核音乐
    result = await db.execute(
        select(Music)
        .where(Music.status == 0)  # 只查下架状态的音乐
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()

    # 4. 返回分页结果
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.put("/music/{music_id}/audit", response_model=MusicAuditResponse)
async def audit_music(
    music_id: int,                             # 要审核的音乐ID
    data: MusicAuditUpdate,                    # 请求体：目标状态
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_database)
):
    # 1. 查找目标音乐
    result = await db.execute(select(Music).where(Music.id == music_id))
    music = result.scalar_one_or_none()

    # 2. 音乐不存在
    if music is None:
        raise HTTPException(status_code=404, detail="音乐不存在")

    # 3. 检查状态值是否合法（只允许 0 或 1）
    if data.status not in [0, 1]:
        raise HTTPException(status_code=400, detail="状态值无效，必须是 0 或 1")

    # 4. 更新音乐状态（1=上架，0=下架）
    music.status = data.status
    await db.flush()

    return music

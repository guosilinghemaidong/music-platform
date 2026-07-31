from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.routers.user import get_database
from pydantic import BaseModel
from app.models.user import User
from app.models.music import Music
from app.models.post import Post
from app.models.post_comment import PostComment
from app.routers.user import get_current_admin
from app.schemas.admin import (
    AdminUserResponse, AdminUserListResponse, UserStatusUpdate, UserStatusResponse,
    AdminMusicResponse, AdminMusicListResponse, MusicAuditUpdate, MusicAuditResponse,
    AdminPostResponse, AdminPostListResponse, PostAuditUpdate, PostAuditResponse
)
from app.schemas.music import MusicCreate


router = APIRouter(prefix="/admin", tags=["管理员"])



# ==================== 用户管理 ====================

@router.get("/users", response_model=AdminUserListResponse)
async def get_user_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    role: str = "user",      # 按角色筛选，默认只查普通用户（传 "all" 查全部）
    keyword: str = "",       # 模糊搜索用户名关键词
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造基础查询（根据 role 参数决定是否筛选）
    query = select(User)
    if role != "all":
        # 默认只查普通用户（role="user"），不显示管理员
        query = query.where(User.role == role)

    # 2. 如果有搜索关键词，按用户名模糊匹配
    if keyword:
        query = query.where(User.username.like(f"%{keyword}%"))

    # 3. 查询符合条件的用户总数
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # 4. 分页查询当前页数据
    offset = (page - 1) * page_size
    result = await db.execute(
        query
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()

    # 5. 返回分页结果
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
async def get_admin_music_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    status: int = -1,        # 状态筛选：-1=全部，0=待审核/已下架，1=已上架
    keyword: str = "",       # 模糊搜索歌曲名关键词
    music_id: int = 0,       # 精确搜索歌曲ID（0 表示不筛选）
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造基础查询（根据 status 参数决定是否筛选）
    query = select(Music)
    if status >= 0:
        # status >= 0 时按具体状态筛选，-1 表示不筛选（查全部）
        query = query.where(Music.status == status)

    # 2. 如果有搜索关键词，按歌曲名模糊匹配
    if keyword:
        query = query.where(Music.title.like(f"%{keyword}%"))

    # 3. 如果指定了 music_id，精确匹配
    if music_id > 0:
        query = query.where(Music.id == music_id)

    # 4. 查询符合条件的音乐总数
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # 5. 分页查询当前页数据
    offset = (page - 1) * page_size
    result = await db.execute(
        query
        .offset(offset)
        .limit(page_size)
    )
    items = result.scalars().all()

    # 6. 返回分页结果
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


# ==================== 管理员添加音乐 ====================

@router.post("/music/add")
async def admin_add_music(
    data: MusicCreate,                         # 请求体：音乐信息（复用 MusicCreate）
    current_user: User = Depends(get_current_admin),  # 需要管理员权限
    db: AsyncSession = Depends(get_database)
):
    # 1. 检查歌名是否已存在
    result = await db.execute(select(Music).where(Music.title == data.title))
    existing = result.scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status_code=400, detail="歌曲名已存在")

    # 2. 创建新音乐，状态设为 0（待审核），不能直接上架
    new_music = Music(**data.model_dump())
    new_music.status = 0
    db.add(new_music)
    await db.flush()

    return {"message": "添加成功，等待审核", "id": new_music.id}


# ==================== 管理员修改用户信息 ====================

class AdminUserUpdate(BaseModel):
    """管理员修改用户信息的请求参数"""
    nickname: str | None = None
    avatar: str | None = None


@router.put("/user/{user_id}/update")
async def admin_update_user(
        user_id: int,
        data: AdminUserUpdate,
        current_user: User = Depends(get_current_admin),
        db: AsyncSession = Depends(get_database)
):
    # 1. 查找目标用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 更新用户信息（只更新传了的字段）
    if data.nickname is not None:
        user.nickname = data.nickname
    if data.avatar is not None:
        user.avatar = data.avatar

    await db.flush()

    return {"message": "修改成功", "id": user.id, "nickname": user.nickname, "avatar": user.avatar}


# ==================== 动态管理 ====================

@router.get("/post/list", response_model=AdminPostListResponse)
async def get_admin_post_list(
    page: int = 1,
    page_size: int = 10,
    status: int = -1,        # -1=全部，0=待审核，1=已通过，2=已拒绝
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造查询
    query = select(Post)
    if status >= 0:
        query = query.where(Post.status == status)

    # 2. 查总数
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # 3. 分页查询，按时间倒序
    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Post.create_time.desc())
        .offset(offset)
        .limit(page_size)
    )
    posts = result.scalars().all()

    # 4. 批量查询发布者信息
    user_ids = list(set([p.user_id for p in posts]))
    user_map = {}
    if user_ids:
        user_result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = user_result.scalars().all()
        user_map = {u.id: (u.nickname or u.username) for u in users}

    # 5. 组装返回数据
    items = []
    for p in posts:
        items.append(AdminPostResponse(
            id=p.id,
            user_id=p.user_id,
            content=p.content,
            images=p.images,
            music_id=p.music_id,
            status=p.status,
            like_count=p.like_count,
            comment_count=p.comment_count,
            create_time=p.create_time,
            username=user_map.get(p.user_id, "未知用户")
        ))

    return AdminPostListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.put("/post/{post_id}/audit", response_model=PostAuditResponse)
async def audit_post(
    post_id: int,
    data: PostAuditUpdate,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database)
):
    # 1. 查找动态
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="动态不存在")

    # 2. 检查状态值（1=通过，2=拒绝）
    if data.status not in [1, 2]:
        raise HTTPException(status_code=400, detail="状态值无效，必须是 1（通过）或 2（拒绝）")

    # 3. 更新状态
    post.status = data.status
    await db.flush()
    return post


@router.delete("/post/{post_id}")
async def admin_delete_post(
    post_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="动态不存在")

    await db.delete(post)
    await db.flush()
    return {"message": "删除成功"}


@router.delete("/post/comment/{comment_id}")
async def admin_delete_post_comment(
    comment_id: int,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_database)
):
    # 1. 查询评论
    result = await db.execute(select(PostComment).where(PostComment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="评论未找到")

    # 2. 更新动态评论计数
    post_result = await db.execute(select(Post).where(Post.id == comment.post_id))
    post = post_result.scalar_one_or_none()
    if post:
        post.comment_count = max(0, post.comment_count - 1)

    # 3. 删除评论
    await db.delete(comment)
    await db.flush()
    return {"message": "评论删除成功"}


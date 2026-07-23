from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db                                  # 数据库会话依赖
from app.routers.user import get_current_user                    # 获取当前登录用户
from app.models.comment import Comment                           # 评论模型
from app.models.user import User                                 # 用户模型（查用户名）
from app.schemas.comment import CommentCreate, CommentResponse   # 评论 Schema


# 创建路由器，前缀 /comment，标签"评论"
router = APIRouter(prefix="/comment", tags=["评论"])


# ==================== 发表评论 ====================
# POST /comment/add，Body 传 { "music_id": 1, "content": "好听！" }
# 需要登录才能评论
@router.post("/add", response_model=CommentResponse)
async def add_comment(
    data: CommentCreate,                                   # 接收 music_id 和 content
    current_user: dict = Depends(get_current_user),        # 获取当前登录用户
    db: AsyncSession = Depends(get_db)                     # 数据库会话
):
    # 1. 创建评论记录，user_id 从当前登录用户获取
    new_comment = Comment(
        user_id=current_user.id,
        music_id=data.music_id,
        content=data.content
    )
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)    # 刷新一下，让 create_time 等数据库自动生成的字段填充进来

    # 2. 查询评论者的用户名（因为返回格式里需要 username）
    user_result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = user_result.scalar_one_or_none()

    # 3. 手动组装返回数据（CommentResponse 里有 username 字段，但 Comment 模型里没有）
    return {
        "id": new_comment.id,
        "user_id": new_comment.user_id,
        "username": user.nickname or user.username if user else "未知用户",
        "content": new_comment.content,
        "music_id": new_comment.music_id,
        "create_time": new_comment.create_time
    }


# ==================== 删除评论 ====================
# DELETE /comment/delete/{comment_id}
# 只能删除自己发的评论，不能删别人的
@router.delete("/delete/{comment_id}")
async def delete_comment(
    comment_id: int,                                       # 要删除的评论ID
    current_user: dict = Depends(get_current_user),        # 获取当前登录用户
    db: AsyncSession = Depends(get_db)                     # 数据库会话
):
    # 1. 查询评论是否存在
    result = await db.execute(
        select(Comment).where(Comment.id == comment_id)
    )
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="评论未找到")

    # 2. 检查是不是本人发的评论（只能删自己的）
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的评论")

    # 3. 删除评论
    await db.delete(comment)
    await db.commit()
    return {"message": "评论删除成功"}


# ==================== 查看评论列表 ====================
# GET /comment/list/{music_id}
# 查看某首歌的所有评论，按时间倒序（最新的在前面）
# 不需要登录也能看评论
@router.get("/list/{music_id}", response_model=list[CommentResponse])
async def get_comment_list(
    music_id: int,                                         # 查看哪首歌的评论
    db: AsyncSession = Depends(get_db)                     # 数据库会话
):
    # 1. 查询这首歌的所有评论，按创建时间倒序排列
    result = await db.execute(
        select(Comment)
        .where(Comment.music_id == music_id)
        .order_by(Comment.create_time.desc())              # 最新的评论排在最前面
    )
    comments = result.scalars().all()

    # 2. 收集所有评论的 user_id，批量查询用户名（避免一条一条查，性能更好）
    user_ids = list(set([c.user_id for c in comments]))    # 去重，拿到不重复的用户ID列表

    if user_ids:
        # 批量查询这些用户的信息
        user_result = await db.execute(
            select(User).where(User.id.in_(user_ids))      # IN 查询，一次拿到所有用户
        )
        users = user_result.scalars().all()
        # 把用户列表转成字典，方便后面按 ID 快速查找：{ 用户ID: 用户名 }
        user_map = {u.id: (u.nickname or u.username) for u in users}
    else:
        user_map = {}

    # 3. 手动组装返回数据（每条评论加上 username）
    comment_list = []
    for c in comments:
        comment_list.append({
            "id": c.id,
            "user_id": c.user_id,
            "username": user_map.get(c.user_id, "未知用户"),  # 从字典里取用户名，取不到就显示"未知用户"
            "content": c.content,
            "music_id": c.music_id,
            "create_time": c.create_time
        })

    return comment_list

import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.routers.user import get_database
from app.routers.user import get_current_user, User
from app.models.post import Post
from app.models.post_like import PostLike
from app.models.post_comment import PostComment
from app.models.music import Music
from app.schemas.post import (
    PostResponse, PostListResponse, PostCreate,
    PostLikeToggle, PostLikeStatus,
    PostCommentCreate, PostCommentResponse
)

router = APIRouter(prefix="/post", tags=["动态"])


# ==================== 发布动态 ====================
# POST /post/add
# 需要登录，status 默认为 0（待审核）
@router.post("/add", response_model=PostResponse)
async def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    # 如果传了 music_id，检查音乐是否存在
    if post_data.music_id is not None:
        result = await db.execute(select(Music).where(Music.id == post_data.music_id))
        music = result.scalar_one_or_none()
        if music is None:
            raise HTTPException(status_code=404, detail="音乐不存在")

    new_post = Post(
        user_id=current_user.id,
        content=post_data.content,
        images=post_data.images,
        music_id=post_data.music_id,
        status=0  # 默认待审核
    )
    db.add(new_post)
    await db.flush()
    await db.refresh(new_post)  # 刷新，让数据库自动生成的 create_time 等字段填充进来

    return PostResponse(
        id=new_post.id,
        user_id=new_post.user_id,
        content=new_post.content,
        images=new_post.images,
        music_id=new_post.music_id,
        status=new_post.status,
        like_count=0,
        comment_count=0,
        create_time=new_post.create_time,
        username=current_user.nickname or current_user.username,
        avatar=current_user.avatar
    )


# ==================== 动态列表 ====================
# GET /post/list
# 只返回 status=1（已通过审核）的动态，按时间倒序
# 支持可选参数 status 给管理员用（管理员可传 0/1/2 筛选）
@router.get("/list", response_model=PostListResponse)
async def get_post_list(
    page: int = 1,
    page_size: int = 10,
    status: int = 1,            # 默认只查已审核通过的
    current_user: User = Depends(get_current_user),  # 需要登录（为了判断是否已点赞）
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造查询（按 status 筛选）
    query = select(Post).where(Post.status == status)

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
        user_map = {u.id: u for u in users}

    # 5. 批量查询当前用户对这些动态的点赞状态
    liked_set = set()
    if current_user and posts:
        post_ids = [p.id for p in posts]
        like_result = await db.execute(
            select(PostLike.post_id).where(
                PostLike.user_id == current_user.id,
                PostLike.post_id.in_(post_ids)
            )
        )
        liked_set = set(like_result.scalars().all())

    # 6. 组装返回数据
    items = []
    for p in posts:
        author = user_map.get(p.user_id)
        items.append(PostResponse(
            id=p.id,
            user_id=p.user_id,
            content=p.content,
            images=p.images,
            music_id=p.music_id,
            status=p.status,
            like_count=p.like_count,
            comment_count=p.comment_count,
            create_time=p.create_time,
            username=(author.nickname or author.username) if author else "未知用户",
            avatar=author.avatar if author else None,
            is_liked=(p.id in liked_set)
        ))

    return PostListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


# ==================== 删除动态 ====================
# DELETE /post/delete/{post_id}
# 只能删除自己的动态
@router.delete("/delete/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if post is None:
        raise HTTPException(status_code=404, detail="动态未找到")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的动态")

    await db.delete(post)
    await db.flush()
    return {"message": "删除成功"}


# ==================== 动态点赞 / 取消点赞 ====================
# POST /post/like/toggle
# Body: { "post_id": 1 }
@router.post("/like/toggle", response_model=PostLikeStatus)
async def toggle_post_like(
    data: PostLikeToggle,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    # 1. 检查动态是否存在
    post_result = await db.execute(select(Post).where(Post.id == data.post_id))
    post = post_result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="动态不存在")

    # 2. 查询当前用户是否已点赞
    existing = await db.execute(
        select(PostLike).where(
            PostLike.user_id == current_user.id,
            PostLike.post_id == data.post_id
        )
    )
    like = existing.scalar_one_or_none()

    if like:
        # 已点赞 → 取消点赞
        await db.delete(like)
        post.like_count = max(0, post.like_count - 1)
        await db.flush()
        return PostLikeStatus(is_liked=False, like_count=post.like_count)
    else:
        # 未点赞 → 添加点赞
        new_like = PostLike(user_id=current_user.id, post_id=data.post_id)
        db.add(new_like)
        post.like_count += 1
        await db.flush()
        return PostLikeStatus(is_liked=True, like_count=post.like_count)


# ==================== 发表评论 ====================
# POST /post/comment/add
# Body: { "post_id": 1, "content": "好看！" }
@router.post("/comment/add", response_model=PostCommentResponse)
async def add_post_comment(
    data: PostCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    # 1. 检查动态是否存在
    post_result = await db.execute(select(Post).where(Post.id == data.post_id))
    post = post_result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status_code=404, detail="动态不存在")

    # 2. 创建评论
    new_comment = PostComment(
        user_id=current_user.id,
        post_id=data.post_id,
        content=data.content
    )
    db.add(new_comment)
    await db.flush()
    await db.refresh(new_comment)  # 刷新，让 create_time 等数据库生成的字段填充进来

    # 3. 更新动态的评论计数
    post.comment_count += 1
    await db.flush()

    return PostCommentResponse(
        id=new_comment.id,
        user_id=new_comment.user_id,
        post_id=new_comment.post_id,
        content=new_comment.content,
        username=current_user.nickname or current_user.username,
        avatar=current_user.avatar,
        create_time=new_comment.create_time
    )


# ==================== 查看评论列表 ====================
# GET /post/comment/list/{post_id}
@router.get("/comment/list/{post_id}", response_model=list[PostCommentResponse])
async def get_post_comment_list(
    post_id: int,
    db: AsyncSession = Depends(get_database)
):
    # 1. 查询该动态的所有评论，按时间倒序
    result = await db.execute(
        select(PostComment)
        .where(PostComment.post_id == post_id)
        .order_by(PostComment.create_time.asc())
    )
    comments = result.scalars().all()

    # 2. 批量查询评论者信息
    user_ids = list(set([c.user_id for c in comments]))
    user_map = {}
    if user_ids:
        user_result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = user_result.scalars().all()
        user_map = {u.id: u for u in users}

    # 3. 组装返回数据
    comment_list = []
    for c in comments:
        author = user_map.get(c.user_id)
        comment_list.append(PostCommentResponse(
            id=c.id,
            user_id=c.user_id,
            post_id=c.post_id,
            content=c.content,
            username=(author.nickname or author.username) if author else "未知用户",
            avatar=author.avatar if author else None,
            create_time=c.create_time
        ))

    return comment_list


# ==================== 删除评论 ====================
# DELETE /post/comment/delete/{comment_id}
# 只能删除自己的评论
@router.delete("/comment/delete/{comment_id}")
async def delete_post_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    # 1. 查询评论
    result = await db.execute(select(PostComment).where(PostComment.id == comment_id))
    comment = result.scalar_one_or_none()
    if comment is None:
        raise HTTPException(status_code=404, detail="评论未找到")

    # 2. 检查是否是自己的评论
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的评论")

    # 3. 删除评论并更新计数
    post_result = await db.execute(select(Post).where(Post.id == comment.post_id))
    post = post_result.scalar_one_or_none()
    if post:
        post.comment_count = max(0, post.comment_count - 1)

    await db.delete(comment)
    await db.flush()
    return {"message": "评论删除成功"}


# ==================== 热门动态（首页推荐） ====================
# GET /post/hot
# 返回点赞数最多的已通过审核动态（默认前 5 条），包含发布者头像
@router.get("/hot")
async def get_hot_posts(
    limit: int = 5,
    db: AsyncSession = Depends(get_database)
):
    # 1. 按点赞数倒序查询已审核通过的动态
    result = await db.execute(
        select(Post)
        .where(Post.status == 1)
        .order_by(Post.like_count.desc())
        .limit(limit)
    )
    posts = result.scalars().all()

    # 2. 批量查询发布者信息（头像 + 昵称）
    user_ids = list(set([p.user_id for p in posts]))
    user_map = {}
    if user_ids:
        user_result = await db.execute(select(User).where(User.id.in_(user_ids)))
        users = user_result.scalars().all()
        user_map = {u.id: u for u in users}

    # 3. 组装返回数据
    return [
        {
            "id": p.id,
            "user_id": p.user_id,
            "content": p.content,
            "images": p.images,
            "music_id": p.music_id,
            "like_count": p.like_count,
            "comment_count": p.comment_count,
            "create_time": p.create_time,
            "username": (user_map[p.user_id].nickname or user_map[p.user_id].username) if p.user_id in user_map else "未知用户",
            "avatar": user_map[p.user_id].avatar if p.user_id in user_map else None
        }
        for p in posts
    ]

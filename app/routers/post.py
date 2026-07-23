from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.routers.user import get_database
from app.models.post import Post
from app.schemas.post import PostResponse, PostListResponse, PostCreate
from app.routers.user import get_current_user, User

router = APIRouter(prefix="/post", tags=["动态"])




@router.post("/add", response_model=PostResponse)
async def create_post(
        post_data: PostCreate,
        current_user: User = Depends(get_current_user),  # 需要登录
        db: AsyncSession = Depends(get_database)
):
    # user_id 从 current_user.id 获取，不让前端传
    new_post = Post(
        user_id=current_user.id,
        content=post_data.content
    )
    db.add(new_post)
    await db.flush()
    await db.refresh(new_post)
    return new_post


@router.get("/list", response_model=PostListResponse)
async def get_post_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    db: AsyncSession = Depends(get_database)
):
    # 1. 计算跳过多少条
    offset = (page - 1) * page_size

    # 2. 查询总数（SELECT COUNT(*) FROM post）
    total_result = await db.execute(select(Post))
    total = len(total_result.scalars().all())

    # 3. 查询当前页数据（SELECT * FROM post LIMIT page_size OFFSET offset）
    result = await db.execute(
        select(Post)
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


@router.delete("/delete/{post_id}")
async def delete_post(
        post_id: int,
        current_user: User = Depends(get_current_user),  # 需要登录
        db: AsyncSession = Depends(get_database)
):
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()
    # 1. 动态不存在
    if post is None:
        raise HTTPException(status_code=404, detail="动态未找到")

    # 2. 检查是否是自己的动态
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能删除自己的动态")
    # 3. 删除动态
    await db.delete(post)
    await db.flush()
    return {"message": "删除成功"}

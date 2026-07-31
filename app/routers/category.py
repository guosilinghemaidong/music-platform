from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.category import Category
from app.schemas.category import CategoryResponse, CategoryListResponse, CategoryCreate, CategoryUpdate


router = APIRouter(prefix="/category", tags=["分类"])


# 获取数据库会话
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@router.get("/list", response_model=CategoryListResponse)
async def get_category_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    keyword: str = "",       # 模糊搜索分类名关键词
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造基础查询
    query = select(Category)

    # 2. 如果有搜索关键词，按分类名模糊匹配
    if keyword:
        query = query.where(Category.name.like(f"%{keyword}%"))

    # 3. 计算跳过多少条
    offset = (page - 1) * page_size

    # 4. 查询总数
    total_result = await db.execute(query)
    total = len(total_result.scalars().all())

    # 5. 查询当前页数据
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


@router.get("/detail/{category_id}", response_model=CategoryResponse)
async def get_category_detail(category_id: int, db: AsyncSession = Depends(get_database)):
    # 根据 ID 查询分类
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="分类未找到")
    return category


@router.post("/create", response_model=CategoryResponse)
async def create_category(category_data: CategoryCreate, db: AsyncSession = Depends(get_database)):
    # 1. 检查是否已存在
    result = await db.execute(select(Category).where(Category.name == category_data.name))
    category = result.scalar_one_or_none()
    if category is not None:
        raise HTTPException(status_code=400, detail="分类已存在")

    # 2. 创建新分类
    new_category = Category(**category_data.model_dump())
    db.add(new_category)
    await db.flush()
    return new_category


@router.put("/update/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category_data: CategoryUpdate, db: AsyncSession = Depends(get_database)):
    # 1. 检查分类是否存在
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="分类未找到")
    # 2. 更新分类信息
    for key, value in category_data.model_dump().items():
        setattr(category, key, value)

    await db.flush()
    return category


@router.delete("/delete/{category_id}")
async def delete_category(category_id: int, db: AsyncSession = Depends(get_database)):
    # 1. 检查分类是否存在
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(status_code=404, detail="分类未找到")
    # 2. 删除分类
    await db.delete(category)
    await db.flush()
    return {"message": "删除成功"}
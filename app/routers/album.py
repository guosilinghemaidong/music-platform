from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.album import Album
from app.schemas.album import AlbumResponse, AlbumListResponse, AlbumCreate, AlbumUpdate


router = APIRouter(prefix="/album", tags=["专辑"])


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


@router.get("/list", response_model=AlbumListResponse)
async def get_album_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    keyword: str = "",       # 模糊搜索专辑名关键词
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造基础查询
    query = select(Album)

    # 2. 如果有搜索关键词，按专辑名模糊匹配
    if keyword:
        query = query.where(Album.name.like(f"%{keyword}%"))

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


@router.get("/detail/{album_id}", response_model=AlbumResponse)
async def get_album_detail(album_id: int, db: AsyncSession = Depends(get_database)):
    # 根据 ID 查询专辑
    result = await db.execute(select(Album).where(Album.id == album_id))
    album = result.scalar_one_or_none()
    if album is None:
        raise HTTPException(status_code=404, detail="专辑未找到")
    return album


@router.post("/create", response_model=AlbumResponse)
async def create_album(album_data: AlbumCreate, db: AsyncSession = Depends(get_database)):
    # 1. 检查是否已存在
    result = await db.execute(select(Album).where(Album.name == album_data.name))
    album = result.scalar_one_or_none()
    if album is not None:
        raise HTTPException(status_code=400, detail="专辑已存在")

    # 2. 创建新专辑
    new_album = Album(**album_data.model_dump())
    db.add(new_album)
    await db.flush()
    return new_album


@router.put("/update/{album_id}", response_model=AlbumResponse)
async def update_album(album_id: int, album_data: AlbumUpdate, db: AsyncSession = Depends(get_database)):
    # 1. 检查专辑是否存在
    result = await db.execute(select(Album).where(Album.id == album_id))
    album = result.scalar_one_or_none()
    if album is None:
        raise HTTPException(status_code=404, detail="专辑未找到")
    # 2. 更新专辑信息
    for key, value in album_data.model_dump().items():
        setattr(album, key, value)

    await db.flush()
    return album


@router.delete("/delete/{album_id}")
async def delete_album(album_id: int, db: AsyncSession = Depends(get_database)):
    # 1. 检查专辑是否存在
    result = await db.execute(select(Album).where(Album.id == album_id))
    album = result.scalar_one_or_none()
    if album is None:
        raise HTTPException(status_code=404, detail="专辑未找到")
    # 2. 删除专辑
    await db.delete(album)
    await db.flush()
    return {"message": "删除成功"}
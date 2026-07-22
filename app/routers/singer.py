from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.singer import Singer
from app.schemas.singer import SingerResponse, SingerListResponse, SingerCreate, SingerUpdate


router = APIRouter(prefix="/singer", tags=["歌手"])

# 复用 user.py 里的 get_database（获取数据库会话）
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


@router.get("/list", response_model=SingerListResponse)
async def get_singer_list(
    page: int = 1,           # 页码，默认第 1 页
    page_size: int = 10,     # 每页数量，默认 10 条
    db: AsyncSession = Depends(get_database)
):
    # 1. 计算跳过多少条
    offset = (page - 1) * page_size

    # 2. 查询总数（SELECT COUNT(*) FROM singer）
    total_result = await db.execute(select(Singer))
    total = len(total_result.scalars().all())

    # 3. 查询当前页数据（SELECT * FROM signer LIMIT page_size OFFSET offset）
    result = await db.execute(
        select(Singer)
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

@router.get("/detail/{singer_id}", response_model=SingerResponse)
async def get_singer_detail(singer_id: int, db: AsyncSession = Depends(get_database)):
    # 根据 ID 查询歌手
    result = await db.execute(select(Singer).where(Singer.id == singer_id))
    singer = result.scalar_one_or_none()
    if singer is None:
        raise HTTPException(status_code=404, detail="歌手未找到")
    return singer


@router.post("/create", response_model=SingerResponse)
async def create_singer(singer_data: SingerCreate, db: AsyncSession = Depends(get_database)):
    # 1. 检查是否已存在
    result = await db.execute(select(Singer).where(Singer.name == singer_data.name))
    singer = result.scalar_one_or_none()
    if singer is not None:
        raise HTTPException(status_code=400, detail="歌手已存在")

    # 2. 创建新歌手
    new_singer = Singer(**singer_data.model_dump())
    db.add(new_singer)
    await db.flush()
    return new_singer


@router.put("/update/{singer_id}", response_model=SingerResponse)
async def update_singer(singer_id: int, singer_data: SingerUpdate, db: AsyncSession = Depends(get_database)):
    # 1. 检查歌手是否存在
    result = await db.execute(select(Singer).where(Singer.id == singer_id))
    singer = result.scalar_one_or_none()
    if singer is None:
        raise HTTPException(status_code=404, detail="歌手未找到")
    # 2. 更新歌手信息
    for key, value in singer_data.model_dump().items():
        setattr(singer, key, value)

    await db.flush()
    return singer

@router.delete("/delete/{singer_id}")
async def delete_singer(singer_id: int, db: AsyncSession = Depends(get_database)):
    # 1. 检查歌手是否存在
    result = await db.execute(select(Singer).where(Singer.id == singer_id))
    singer = result.scalar_one_or_none()
    if singer is None:
        raise HTTPException(status_code=404, detail="歌手未找到")
    # 2. 删除歌手
    await db.delete(singer)
    await db.flush()
    return {"message": "删除成功"}

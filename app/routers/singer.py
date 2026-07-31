from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.singer import Singer
from app.models.music import Music
from app.models.album import Album
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
    keyword: str = "",       # 模糊搜索歌手名关键词
    db: AsyncSession = Depends(get_database)
):
    # 1. 构造基础查询
    query = select(Singer)

    # 2. 如果有搜索关键词，按歌手名模糊匹配
    if keyword:
        query = query.where(Singer.name.like(f"%{keyword}%"))

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

@router.get("/detail/{singer_id}", response_model=SingerResponse)
async def get_singer_detail(singer_id: int, db: AsyncSession = Depends(get_database)):
    # 根据 ID 查询歌手
    result = await db.execute(select(Singer).where(Singer.id == singer_id))
    singer = result.scalar_one_or_none()
    if singer is None:
        raise HTTPException(status_code=404, detail="歌手未找到")
    return singer


# 歌手完整详情（歌手信息 + 歌曲列表 + 专辑列表）
# 用于前端歌手详情页展示
@router.get("/full/{singer_id}")
async def get_singer_full_detail(singer_id: int, db: AsyncSession = Depends(get_database)):
    # 1. 查询歌手基本信息
    result = await db.execute(select(Singer).where(Singer.id == singer_id))
    singer = result.scalar_one_or_none()
    if singer is None:
        raise HTTPException(status_code=404, detail="歌手未找到")

    # 2. 查询该歌手的歌曲列表（只查已上架的，status=1）
    music_result = await db.execute(
        select(Music).where(Music.singer_id == singer_id, Music.status == 1)
    )
    songs = music_result.scalars().all()

    # 3. 查询该歌手的专辑列表
    album_result = await db.execute(
        select(Album).where(Album.singer_id == singer_id)
    )
    albums = album_result.scalars().all()

    # 4. 把 ORM 对象转成普通字典（避免 session 关闭后序列化触发懒加载报错）
    singer_dict = {c.name: getattr(singer, c.name) for c in Singer.__table__.columns}
    songs_list = [{c.name: getattr(s, c.name) for c in Music.__table__.columns} for s in songs]
    albums_list = [{c.name: getattr(a, c.name) for c in Album.__table__.columns} for a in albums]

    return {
        "singer": singer_dict,
        "songs": songs_list,
        "albums": albums_list
    }


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

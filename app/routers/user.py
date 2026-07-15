from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse

# 创建路由器
router = APIRouter(prefix="/user", tags=["用户"])


# 依赖项：获取数据库会话
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


# 注册接口
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_database)):
    # 1. 先检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # 用户名已存在，返回错误
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 2. 创建新用户对象
    new_user = User(
        username=user_data.username,
        password=user_data.password,  # 暂时明文存储，后面改成加密
        nickname=user_data.nickname,
    )

    # 3. 添加到数据库
    db.add(new_user)
    await db.flush()  # 刷新一下，让 id 生成出来

    # 4. 返回新用户信息
    return new_user

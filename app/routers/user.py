from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.utils.auth import verify_password, create_access_token
from app.schemas.user import UserRegister, UserResponse, UserLogin, TokenResponse, UserUpdate
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM
from fastapi.security import APIKeyHeader



# 创建路由器
router = APIRouter(prefix="/user", tags=["用户"])
# 定义安全方案：从请求头的 Authorization 字段取 Token
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)



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



# 登录接口
@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_database)):
    # 1. 查找用户是否存在
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()

    # 2. 用户不存在
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 3. 验证密码是否正确
    if not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 4. 生成 Token
    access_token = create_access_token(data={"sub": user.username})

    # 5. 返回 Token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }




# 依赖函数：从 Token 中获取当前用户
async def get_current_user(
    authorization: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_database)
):
    # 1. 检查是否传了 Token
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证信息")

    # 2. 取出 Token（去掉 "Bearer " 前缀）
    token = authorization.split(" ")[1]

    try:
        # 3. 解析 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Token 无效")

    except JWTError:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")

    # 4. 从数据库查询用户
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


# 获取当前登录用户的信息
@router.get("/me", response_model=UserResponse)
async def get_my_info(current_user: User = Depends(get_current_user)):
    # current_user 就是当前登录的用户（从 Token 里解析出来的）
    return current_user


# 修改当前登录用户的信息
@router.put("/me", response_model=UserResponse)
async def update_my_info(
    user_data: UserUpdate ,                              # 要修改的字段
    current_user: User = Depends(get_current_user),     # 当前登录用户
    db: AsyncSession = Depends(get_database)            # 数据库会话
):
    # 只更新传了的字段（不为 None 的才改）
    if user_data.nickname is not None:
        current_user.nickname = user_data.nickname
    if user_data.avatar is not None:
        current_user.avatar = user_data.avatar

    # 提交修改
    await db.flush()
    return current_user

# 根据 ID 查看其他用户信息（不需要登录）
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_database)):
    # 根据 ID 查询用户
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return user
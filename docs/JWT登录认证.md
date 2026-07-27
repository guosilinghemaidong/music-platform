C:\Users\41434\Desktop\FastAPI_base\docs\Day4-JWT登录认证.md
# Day 4 代码逐行分析

## 文件 1：app/utils/auth.py

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.config import SECRET_KEY, ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_minutes: int = 30) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

### 导入解释

| 导入 | 是什么 | 作用 |
|------|--------|------|
| `CryptContext` | passlib 的类 | 提供密码加密/验证功能 |
| `datetime` | Python 标准库 | 获取当前时间 |
| `timedelta` | Python 标准库 | 计算时间差（如"30分钟后"） |
| `jwt` | python-jose 库 | 生成和解析 JWT Token |
| `SECRET_KEY, ALGORITHM` | 我们的配置 | JWT 密钥和算法 |

### 密码加密部分

| 代码 | 含义 |
|------|------|
| `CryptContext(schemes=["bcrypt"])` | 创建密码上下文，使用 bcrypt 算法 |
| `pwd_context.hash(password)` | 把明文密码加密成哈希字符串 |
| `pwd_context.verify(明文, 哈希)` | 对比明文和哈希是否匹配，返回 True/False |

> 💡 **bcrypt 特点：** 同样的密码每次加密结果不同（有随机盐），但验证时能正确匹配。

### Token 生成部分

| 代码 | 含义 |
|------|------|
| `data: dict` | 要加密的数据，一般是 `{"sub": "用户名"}` |
| `expires_minutes=30` | 过期时间，默认 30 分钟 |
| `to_encode.copy()` | 复制数据（不修改原数据） |
| `datetime.utcnow()` | 获取当前 UTC 时间 |
| `timedelta(minutes=30)` | 30 分钟的时间差 |
| `to_encode.update({"exp": expire})` | 把过期时间加入数据 |
| `jwt.encode(...)` | 用密钥加密，生成 Token 字符串 |
| `SECRET_KEY` | 加密密钥 |
| `algorithm=ALGORITHM` | 加密算法（HS256） |

> 💡 **Token 内容：** 加密后包含用户名和过期时间，后端可以解析，前端看不到明文。

---

## 文件 2：app/schemas/user.py（Day 4 新增）

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

### 逐行解释

| 类 | 作用 |
|---|------|
| `UserLogin` | 验证登录时前端传的数据 |
| `TokenResponse` | 定义登录成功后返回的数据格式 |

| 字段 | 含义 |
|------|------|
| `access_token` | Token 字符串 |
| `token_type` | 固定是 "bearer"（JWT 标准类型） |

---

## 文件 3：app/routers/user.py（Day 4 新增）

from app.utils.auth import verify_password, create_access_token
from app.schemas.user import UserLogin, TokenResponse
from jose import jwt, JWTError
from app.config import SECRET_KEY, ALGORITHM
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

### 新增导入解释

| 导入 | 作用 |
|------|------|
| `verify_password` | 验证密码 |
| `create_access_token` | 生成 Token |
| `jwt, JWTError` | 解析 Token |
| `APIKeyHeader` | Swagger 认证方案 |

### APIKeyHeader 解释

| 参数 | 含义 |
|------|------|
| `name="Authorization"` | 从请求头的 Authorization 字段取 Token |
| `auto_error=False` | 没 Token 时不自动报错，手动处理 |

> 💡 **作用：** 让 Swagger 显示 Authorize 按钮，方便测试需要登录的接口。

---

### 登录接口

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    if not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

### 逐行解释

| 代码 | 含义 |
|------|------|
| `@router.post("/login")` | POST 请求，路径 `/user/login` |
| `response_model=TokenResponse` | 返回 Token 格式 |
| `user_data: UserLogin` | 验证登录参数 |
| `select(User).where(...)` | 查询用户（ORM → SQL） |
| `scalar_one_or_none()` | 取第一条，没有返回 None |
| `if not user:` | 用户不存在 |
| `verify_password(...)` | 验证密码是否正确 |
| `create_access_token(data={"sub": ...})` | 生成 Token，sub 存用户名 |
| `return {...}` | 返回 Token 和类型 |

> 💡 **安全细节：** 用户不存在和密码错误返回同样的信息 `"用户名或密码错误"`，不告诉攻击者具体是哪个错了。

---

### 获取当前用户依赖函数

async def get_current_user(
    authorization: str = Depends(api_key_header),
    db: AsyncSession = Depends(get_database)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供有效的认证信息")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token 无效")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token 无效或已过期")

    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user

### 逐行解释

| 代码 | 含义 |
|------|------|
| `authorization: str = Depends(api_key_header)` | 从请求头取 Authorization 值 |
| `startswith("Bearer ")` | 检查格式是否正确 |
| `authorization.split(" ")[1]` | 去掉 "Bearer " 前缀，拿到纯 Token |
| `jwt.decode(token, SECRET_KEY, ...)` | 用密钥解析 Token |
| `payload.get("sub")` | 从 Token 取出用户名 |
| `except JWTError:` | Token 解析失败（过期/被篡改） |
| `select(User).where(...)` | 从数据库查用户 |
| `return user` | 返回当前登录用户 |

> 💡 **这是一个"依赖函数"：** 后面需要登录的接口用 `current_user: User = Depends(get_current_user)` 就能自动拿到当前用户。

---

## Day 4 总结

| 文件 | 新增内容 | 作用 |
|------|---------|------|
| `utils/auth.py` | 密码加密 + Token 生成 | 安全工具 |
| `schemas/user.py` | UserLogin + TokenResponse | 登录数据验证 |
| `routers/user.py` | 登录接口 + get_current_user | 认证逻辑 |
| `config.py` | SECRET_KEY + ALGORITHM | JWT 配置 |

**Day 4 的本质：** 实现"登录 → 发 Token → 后续请求验证 Token"的完整认证流程。

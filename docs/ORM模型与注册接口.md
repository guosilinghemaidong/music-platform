C:\Users\41434\Desktop\FastAPI_base\docs\Day3-ORM模型与注册接口.md
# Day 3 代码逐行分析

## 文件 1：app/models/base.py

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

### 逐行解释

| 代码 | 含义 |
|------|------|
| `from sqlalchemy.orm import DeclarativeBase` | 导入声明式基类 |
| `class Base(DeclarativeBase):` | 创建基类，继承 SQLAlchemy 的声明式基类 |
| `pass` | 什么都不做，只是占位 |

> 💡 **为什么不直接继承 DeclarativeBase？**
> - 所有模型继承同一个 Base，SQLAlchemy 知道它们属于同一个数据库
> - 减少导入，其他文件只需要 `from app.models.base import Base`
> - 方便扩展，以后想在基类加公共字段只改 base.py
> - 建表方便，`Base.metadata.create_all()` 一次性建所有表

---

## 文件 2：app/models/user.py

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
import datetime
from app.models.base import Base

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户ID")
    username: Mapped[str] = mapped_column(String(50), nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(100), nullable=False, comment="密码")
    nickname: Mapped[str] = mapped_column(String(50), nullable=True, comment="昵称")
    avatar: Mapped[str] = mapped_column(String(255), nullable=True, comment="头像路径")
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user", comment="角色")
    status: Mapped[int] = mapped_column(nullable=False, default=1, comment="状态")
    create_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), comment="创建时间")
    update_time: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")

### 导入解释

| 导入 | 是什么 | 作用 |
|------|--------|------|
| `Mapped` | 类型注解 | 告诉 Python 这个字段是什么类型 |
| `mapped_column` | 函数 | 定义列的属性（主键、长度、是否可空等） |
| `String` | 类型 | 对应数据库的 VARCHAR |
| `DateTime` | 类型 | 对应数据库的 DATETIME |
| `func` | 函数集合 | 提供数据库函数（如 `func.now()` = 当前时间） |
| `Base` | 基类 | 所有模型都继承它 |

### 逐字段拆解

| ORM 代码 | 对应数据库 | 说明 |
|----------|-----------|------|
| `__tablename__ = "user"` | 表名 user | 指定对应的数据库表 |
| `id: Mapped[int]` | `id INT` | Python 类型 int |
| `primary_key=True` | `PRIMARY KEY` | 主键 |
| `autoincrement=True` | `AUTO_INCREMENT` | 自增 |
| `String(50)` | `VARCHAR(50)` | 字符串，最大 50 字符 |
| `nullable=False` | `NOT NULL` | 不能为空 |
| `nullable=True` | `DEFAULT NULL` | 可以为空 |
| `default="user"` | Python 层面默认值 | 新建对象没传值时用 |
| `server_default=func.now()` | `DEFAULT CURRENT_TIMESTAMP` | 数据库层面默认值 |
| `onupdate=func.now()` | `ON UPDATE CURRENT_TIMESTAMP` | 更新时自动刷新时间 |

> 💡 **`default` vs `server_default`：**
> - `default` → Python 层面，代码里没传值时用
> - `server_default` → 数据库层面，SQL 里的 DEFAULT

---

## 文件 3：app/schemas/user.py（Day 3 部分）

from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str
    nickname: str = None

class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str = None
    role: str

    class Config:
        from_attributes = True

### UserRegister 逐行解释

| 代码 | 含义 |
|------|------|
| `class UserRegister(BaseModel):` | 继承 BaseModel，自动获得数据验证能力 |
| `username: str` | 必填，必须是字符串 |
| `password: str` | 必填，必须是字符串 |
| `nickname: str = None` | 可选，有默认值 None |

> 💡 **BaseModel 自动做的事：**
> - 检查 username 有没有传 → 没传就报错
> - 检查 password 是不是字符串 → 不是就报错或尝试转换
> - nickname 没传就用 None

### UserResponse 逐行解释

| 代码 | 含义 |
|------|------|
| `id: int` | 返回时包含 id |
| `username: str` | 返回时包含 username |
| **没有 password** | 密码不返回给前端！ |
| `class Config:` | Pydantic 配置类 |
| `from_attributes = True` | 让 Pydantic 能从 ORM 对象里用 `.` 取属性 |

> 💡 **为什么需要 `from_attributes = True`？**
> - 接口返回的是 SQLAlchemy 的 User 对象（用 `.username` 取属性）
> - Pydantic 默认只能从字典取（用 `["username"]`）
> - 加了这行后，Pydantic 就知道用 `.` 来取 ORM 对象的属性

---

## 文件 4：app/routers/user.py（Day 3 部分）

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import UserRegister, UserResponse

router = APIRouter(prefix="/user", tags=["用户"])

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

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_database)):
    result = await db.execute(select(User).where(User.username == user_data.username))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")

    new_user = User(
        username=user_data.username,
        password=user_data.password,
        nickname=user_data.nickname,
    )

    db.add(new_user)
    await db.flush()

    return new_user

### 导入解释

| 导入 | 作用 |
|------|------|
| `APIRouter` | 创建路由器（相当于一个迷你版 FastAPI） |
| `Depends` | 依赖注入（自动传入数据库会话） |
| `AsyncSession` | 数据库会话类型 |
| `select` | SQLAlchemy 查询语句 |
| `AsyncSessionLocal` | 会话工厂（用来生成 session） |
| `User` | ORM 模型（对应 user 表） |
| `UserRegister, UserResponse` | 数据验证模型 |

### 路由器解释

| 参数 | 含义 |
|------|------|
| `prefix="/user"` | 这个路由器下所有接口都以 `/user` 开头 |
| `tags=["用户"]` | Swagger 文档里的分组标签 |

### get_database 逐行解释

| 代码 | 含义 |
|------|------|
| `async def get_database():` | 异步生成器函数（作为依赖项） |
| `async with AsyncSessionLocal() as session:` | 从工厂拿一个 session |
| `yield session` | 把 session 交给接口使用 |
| `await session.commit()` | 接口用完后，提交事务 |
| `except Exception:` | 如果有异常 |
| `await session.rollback()` | 回滚（撤销修改） |
| `finally:` | 无论如何都执行 |
| `await session.close()` | 关闭 session |

> 💡 **这是一个"依赖项"：** 后面接口用 `Depends(get_database)` 就能自动拿到 session，不用每次手动写打开/关闭的逻辑。

### 注册接口逐行解释

| 代码 | 含义 |
|------|------|
| `@router.post("/register")` | POST 请求，完整路径是 `/user/register` |
| `response_model=UserResponse` | 返回数据按 UserResponse 格式过滤（去掉密码） |
| `user_data: UserRegister` | FastAPI 自动用 UserRegister 验证前端传来的 JSON |
| `db: AsyncSession = Depends(get_database)` | 自动注入数据库会话 |
| `select(User)` | 生成 SQL：`SELECT * FROM user` |
| `.where(User.username == user_data.username)` | 加上条件：`WHERE username = 'xxx'` |
| `await db.execute(...)` | 异步执行 SQL |
| `result.scalar_one_or_none()` | 取第一条记录，没有返回 None |
| `raise HTTPException(...)` | 抛出 HTTP 错误 |
| `status_code=400` | 400 = 请求错误（客户端的问题） |
| `User(...)` | 创建 ORM 对象（此时还没存到数据库） |
| `db.add(new_user)` | 把对象加入 session（标记为"待插入"） |
| `await db.flush()` | 刷新到数据库，让 id 生成出来（但还没 commit） |
| `return new_user` | 返回新用户，FastAPI 自动用 UserResponse 过滤 |

> 💡 **ORM 翻译成 SQL：**
> ORM 写法
select(User).where(User.username == user_data.username)
等价的 SQL
SELECT * FROM user WHERE username = 'test'

> 💡 **`flush` vs `commit`：**
> - `flush` → 发送到数据库，但还在事务里，可以回滚
> - `commit` → 真正提交，数据永久保存

---

## Day 3 总结

| 文件 | 核心内容 | 一句话理解 |
|------|---------|-----------|
| `models/base.py` | 声明式基类 | 所有模型的"爸爸" |
| `models/user.py` | User 模型 | Python 版的 user 表 |
| `schemas/user.py` | UserRegister + UserResponse | 验证输入 + 过滤输出 |
| `routers/user.py` | 注册接口 + get_database | 业务逻辑 + 数据库会话管理 |

**Day 3 的本质：** 把数据库表映射到 Python 类，然后写第一个接口，实现"前端传数据 → 验证 → 存数据库 → 返回结果"的完整流程。

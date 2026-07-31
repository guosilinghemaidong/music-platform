from pydantic import BaseModel


# 注册时前端需要传的参数
class UserRegister(BaseModel):
    username: str    # 用户名
    password: str    # 密码
    nickname: str | None = None   # 昵称（可选）


# 注册成功后返回给前端的数据
class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str | None = None    # 昵称（可能为空）
    avatar: str | None = None      # 头像路径（可能为空）
    signature: str | None = None   # 个性签名（可能为空）
    role: str

    # 让 Pydantic 模型支持从 ORM 对象转换
    class Config:
        from_attributes = True


# 登录时前端传的参数
class UserLogin(BaseModel):
    username: str
    password: str


# 登录成功后返回的 Token
class TokenResponse(BaseModel):
    access_token: str   # Token 字符串
    token_type: str     # Token 类型，固定是 "bearer"

# 修改个人信息时要传的参数（都是可选的）
class UserUpdate(BaseModel):
    nickname: str | None = None    # 昵称
    avatar: str | None = None      # 头像
    signature: str | None = None   # 个性签名


# 修改密码时前端需要传的参数
class PasswordUpdate(BaseModel):
    old_password: str   # 旧密码（验证身份用）
    new_password: str   # 新密码
from pydantic import BaseModel


# 注册时前端需要传的参数
class UserRegister(BaseModel):
    username: str    # 用户名
    password: str    # 密码
    nickname: str = None   # 昵称（可选）


# 注册成功后返回给前端的数据
class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str = None
    role: str

    # 让 Pydantic 模型支持从 ORM 对象转换
    class Config:
        from_attributes = True

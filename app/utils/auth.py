from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.config import SECRET_KEY, ALGORITHM


# 创建密码加密上下文，使用 bcrypt 算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# 加密密码：把明文密码变成加密后的字符串
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# 验证密码：把输入的密码和数据库里存的加密密码做对比
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# 生成 JWT Token
def create_access_token(data: dict, expires_minutes: int = 30) -> str:
    # 1. 复制一份数据
    to_encode = data.copy()

    # 2. 设置过期时间：当前时间 + 30 分钟
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    # 3. 用密钥加密，生成 Token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

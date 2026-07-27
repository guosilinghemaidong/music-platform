Day2   26.7.15


今日目标： 
1.写 models/user.py（User 模型类,对应 Navicat 里的表,继承Base类,方便可以后续验证一些参数）
2.写 schemas/user.py（注册时要验证参数格式）
3.写 routers/user.py（注册接口 POST /register）
4.在 main.py 里注册路由

完成情况:均完成

笔记:
1.[models/user.py]文件里:
    Mapped[xxx]代表python类型
    String(50) 对应数据库的 VARCHAR(50)
    每个 mapped_column 对应表里的一个字段
    nullable=False 对应 NOT NULL
    server_default=func.now() 对应 DEFAULT CURRENT_TIMESTAMP
固定语法格式
2.[schemas/user.py]文件里:
    UserRegister继承BaseModel类,实现验证数据的功能
    UserResponse返回给前端的数据
    from_attributes = True:
        让 Pydantic 能从 ORM 对象（用 . 取属性）中读取数据 
        否则 Pydantic 只能从字典（用 [] 取键）中读取
        只要 response_model 要接收 ORM 对象，就必须加这个
3.[routers/user.py]文件里是注册接口


额外完成:
用户登录 + JWT 认证
目标： 能登录，能拿到 Token
[ ] 安装 python-jose 和 passlib[bcrypt]
[ ] 写密码加密和验证的工具函数（utils/auth.py）
[ ] 写登录接口 POST /login（返回 Token）
[ ] 写一个"获取当前用户"的依赖函数（后面每个接口都要用）

问题:
bcrypt 哈希长度不对
现象： ValueError: malformed bcrypt hash (checksum must be exactly 31 chars)
原因： 复制哈希值时带了多余的空格，导致长度不是标准的 60 个字符
解决： 重新生成时注意完整复制
教训： 复制字符串时要小心前后空格，可以用 LENGTH() 验证长度是否正确


用户登录：
前端传 username + password
    ↓
schemas: UserLogin 验证格式
    ↓
routers: 查数据库找用户
    ↓
utils: verify_password 验证密码
    ↓
utils: create_access_token 生成 Token
    ↓
schemas: TokenResponse 格式化返回
    ↓
前端收到 Token，保存起来

后续请求：
前端带上 Authorization: Bearer xxxxx
    ↓
routers: get_current_user 解析 Token
    ↓
拿到当前用户，执行操作

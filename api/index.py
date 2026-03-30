# 在 api/index.py 文件中添加以下代码

# 模拟用户数据
fake_users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "name": "管理员",
        "role": "admin",
        "status": "active",
        "password": "admin123"
    }
}

# 简单的登录 API
@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = None):
    try:
        print(f"Login attempt for user: {form_data.username}")
        
        # 检查用户是否存在
        user = fake_users_db.get(form_data.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查密码
        if user["password"] != form_data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if user["status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # 简单返回 token
        return {"access_token": "test-token", "token_type": "bearer"}
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise

# 添加获取用户信息的 API
@app.get("/api/auth/me")
async def get_me():
    try:
        # 返回模拟的管理员用户信息
        return {
            "id": 1,
            "username": "admin",
            "name": "管理员",
            "role": "admin",
            "status": "active"
        }
    except Exception as e:
        print(f"Get me error: {e}")
        import traceback
        traceback.print_exc()
        raise

# 根路径
@app.get("/")
async def root():
    return {"message": "SA学生作业记录
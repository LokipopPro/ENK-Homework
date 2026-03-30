# 修改 api/index.py 文件
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import sys

# 添加日志
print("Starting API server...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# 简化版本：直接实现登录 API
app = FastAPI(
    title="SA学生作业记录管理系统",
    description="用于SA老师记录学生每周英语作业完成情况的系统",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟用户数据
fake_users_db = {
    "admin": {
        "username": "admin",
        "name": "管理员",
        "role": "admin",
        "status": "active",
        "password": "admin123"  # 实际环境中应该使用密码哈希
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
        
        # 简单返回 token（实际环境中应该使用 JWT）
        return {"access_token": "test-token", "token_type": "bearer"}
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise

# 根路径
@app.get("/")
async def root():
    return {"message": "SA学生作业记录管理系统 API", "version": "1.0.0"}

# 健康检查
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Vercel Serverless Functions 入口
from mangum import Mangum

handler = Mangum(app)
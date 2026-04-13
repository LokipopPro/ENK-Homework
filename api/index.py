from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import sys

# 添加日志
print("Starting API server...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# 导入数据库相关模块
try:
    from app.models import Base
    from app.api import api_router
    from app.utils import engine, get_password_hash, get_db, create_access_token, decode_access_token, verify_password
    from app.models import User
    print("Successfully imported modules")
except Exception as e:
    print(f"Error importing modules: {e}")
    import traceback
    traceback.print_exc()

# 创建FastAPI应用
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

# 配置OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 数据库初始化
def init_database():
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # 创建默认管理员账号
        db = Session(bind=engine)
        try:
            # 检查是否已存在管理员账号
            admin = db.query(User).filter(User.username == "admin").first()
            if not admin:
                # 创建默认管理员
                admin = User(
                    username="admin",
                    password_hash=get_password_hash("123456"),
                    name="管理员",
                    role="admin",
                    status="active"
                )
                db.add(admin)
                db.commit()
                print("默认管理员账号创建成功: username=admin, password=123456")
            else:
                print("管理员账号已存在")
        finally:
            db.close()
    except Exception as e:
        print(f"Database initialization error: {e}")
        import traceback
        traceback.print_exc()

# 执行数据库初始化
init_database()

# 验证token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return user

# 登录 API
@app.post("/api/auth/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    try:
        print(f"Login attempt for user: {form_data.username}")
        
        # 检查用户是否存在
        user = db.query(User).filter(User.username == form_data.username).first()
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        print(f"Login error: {e}")
        import traceback
        traceback.print_exc()
        raise

# 获取用户信息 API
@app.get("/api/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    try:
        # 返回当前用户信息
        return {
            "id": current_user.id,
            "username": current_user.username,
            "name": current_user.name,
            "role": current_user.role,
            "status": current_user.status
        }
    except Exception as e:
        print(f"Get me error: {e}")
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

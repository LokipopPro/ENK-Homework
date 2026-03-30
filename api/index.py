from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models import Base
from app.api import auth, users, students, homework, statistics, export
from app.utils import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时创建数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时的清理工作
    pass

app = FastAPI(
    title="SA学生作业记录管理系统",
    description="用于SA老师记录学生每周英语作业完成情况的系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/auth", tags=["认证"])
app.include_router(users.router, prefix="/users", tags=["用户管理"])
app.include_router(students.router, prefix="/students", tags=["学生管理"])
app.include_router(homework.router, prefix="/homework", tags=["作业管理"])
app.include_router(statistics.router, prefix="/statistics", tags=["统计分析"])
app.include_router(export.router, prefix="/export", tags=["数据导出"])

@app.get("/")
async def root():
    return {"message": "SA学生作业记录管理系统 API"}

# Vercel Serverless Functions 入口
from mangum import Mangum

handler = Mangum(app)
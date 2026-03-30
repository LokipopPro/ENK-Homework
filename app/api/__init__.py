from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .students import router as students_router
from .homework import router as homework_router
from .statistics import router as statistics_router
from .export import router as export_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户管理"])
api_router.include_router(students_router, prefix="/students", tags=["学生管理"])
api_router.include_router(homework_router, prefix="/homework", tags=["作业管理"])
api_router.include_router(statistics_router, prefix="/statistics", tags=["统计分析"])
api_router.include_router(export_router, prefix="/export", tags=["数据导出"])
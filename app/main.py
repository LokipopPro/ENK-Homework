from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.models import Base
from app.utils import engine, get_password_hash
from sqlalchemy.orm import Session

# 创建FastAPI应用
app = FastAPI(
    title="SA学生作业记录管理系统",
    description="用于SA老师记录学生每周英语作业完成情况的系统",
    version="1.0.0"
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
app.include_router(api_router, prefix="/api")

# 初始化数据库
@app.on_event("startup")
def startup_event():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建默认管理员账号
    db = Session(bind=engine)
    try:
        from app.models import User
        # 检查是否已存在管理员账号
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            # 创建默认管理员
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                name="管理员",
                role="admin",
                status="active"
            )
            db.add(admin)
            db.commit()
            print("默认管理员账号创建成功: username=admin, password=admin123")
        
        # 创建默认作业类型
        from app.models import HomeworkType
        default_types = ["语音", "纸质", "听力", "阅读"]
        for type_name in default_types:
            existing_type = db.query(HomeworkType).filter(HomeworkType.name == type_name).first()
            if not existing_type:
                new_type = HomeworkType(name=type_name)
                db.add(new_type)
        
        # 创建默认作业周期
        from app.models import HomeworkCycle
        default_cycles = ["每周", "每课", "每月"]
        for cycle_name in default_cycles:
            existing_cycle = db.query(HomeworkCycle).filter(HomeworkCycle.name == cycle_name).first()
            if not existing_cycle:
                new_cycle = HomeworkCycle(name=cycle_name)
                db.add(new_cycle)
        
        db.commit()
    finally:
        db.close()

# 根路径
@app.get("/")
def read_root():
    return {"message": "SA学生作业记录管理系统 API", "version": "1.0.0"}

# 健康检查
@app.get("/health")
def health_check():
    return {"status": "healthy"}
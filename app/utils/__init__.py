from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sa_system.db")

# 根据数据库类型设置不同的连接参数
if DATABASE_URL.startswith("sqlite"):
    # 在Vercel上使用内存SQLite
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 密码加密
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 密码工具
def verify_password(plain_password, hashed_password):
    # 确保密码长度不超过72字节
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    # 确保密码长度不超过72字节
    password = password[:72]
    return pwd_context.hash(password)

# JWT工具
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# 计算正确率
def calculate_accuracy(correct_questions: int, total_questions: int) -> float:
    if total_questions == 0:
        return 0.0
    return round((correct_questions / total_questions) * 100, 2)

# 计算错误题数
def calculate_incorrect(correct_questions: int, total_questions: int) -> int:
    return total_questions - correct_questions

# 检查是否逾期
def check_overdue(grading_date: datetime) -> bool:
    today = datetime.now().date()
    grading_date = grading_date.date() if hasattr(grading_date, 'date') else grading_date
    days_diff = (today - grading_date).days
    return days_diff > 3
# 数据库配置
DATABASE_URL = "mysql+pymysql://admin:Admin123@172.17.0.9:3306/enk-homework-0g6lvl3rfc673bbd"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
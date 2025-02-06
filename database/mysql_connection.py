from sqlalchemy import create_engine, text, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
import os       
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수에서 MySQL 접속 정보 가져오기
user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT")
db = os.getenv("DB_NAME")

# MySQL 연결 URL
DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

# SQLAlchemy 엔진 및 세션 설정
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


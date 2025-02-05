from sqlalchemy import create_engine, text       #Mysql 데이터베이스 연결 객체 생성 함수
from sqlalchemy.orm import sessionmaker     #데이터베이스 세션관리 객체
from sqlalchemy.ext.declarative import declarative_base

import os       
from dotenv import load_dotenv

load_dotenv()       #MYSQL접속 정보 들어있는 env파일 로드하기

user = os.getenv("DB_USER", "root")
passwd = os.getenv("DB_PASSWD", "rootpass")
host = os.getenv("DB_HOST", "127.0.0.1")
port = os.getenv("DB_PORT", 3306)
db = os.getenv("DB_NAME", "mydatabase")

DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


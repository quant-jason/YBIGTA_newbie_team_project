from fastapi import Depends
from sqlalchemy.orm import Session
from database.mysql_connection import SessionLocal
from app.user.user_repository import UserRepository
from app.user.user_service import UserService
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    """요청이 들어올 때마다 새로운 DB 세션을 생성하고 반환"""
    db = SessionLocal()
    try:
        yield db  # 세션을 제공하지만 commit/rollback은 하지 않음
    finally:
        db.rollback()  # 세션이 닫힐 때 롤백을 수행
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """UserRepository가 MySQL과 연결되도록 수정"""
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    """UserService도 UserRepository와 함께 주입"""
    return UserService(repo)

from typing import Optional
from sqlalchemy.orm import Session
from app.user.user_schema import User
from database.mysql_connection import SessionLocal
from sqlalchemy import text


class UserRepository:
    def __init__(self, db: Optional[Session] = None):
        """
        MYSQL 세션 설정, DB가 없다면 SessionLocal
        """
        self.db = db or SessionLocal()      #db가 없다면 SessionLocal() 실행

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        email 기반 유저 정보 조회
        """
        sql = text("SELECT email, password, username FROM users WHERE email = :email")      #email로 입력받은 데이터에 해당하는 열을 가져오는 sql 문장을 구성
        result = self.db.execute(sql, {"email" : email}).fetchone()     #sql 구문에서 email가 매칭되는 한 개의 결과만 가져오는 sql문 수행
        
        if result:
            return User(email=result.email, password=result.password, username=result.username)
        
        return None

    def save_user(self, user: User) -> User:
        existing_user = self.get_user_by_email(user.email)

        if existing_user:
            sql = text("""
                UPDATE users 
                SET password = :password, username = :username 
                WHERE email = :email
            """)
        else:
            sql = text("""
                INSERT INTO users (email, password, username) 
                VALUES (:email, :password, :username)
            """)
        
        self.db.execute(sql, {"email": user.email, "password": user.password, "username": user.username})
        self.db.commit()
        return user

    def delete_user(self, user: User) -> User:
        sql = text("DELETE FROM users WHERE email = :email")
        self.db.execute(sql, {"email": user.email})
        self.db.commit()
        return user
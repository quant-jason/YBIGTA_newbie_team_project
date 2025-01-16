from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        user = self.repo.get_user_by_email(user_login.email)
        if not user:
            raise ValueError("User Not Found.")
        if user_login.password != user.password:
            raise ValueError("Invalid ID/PW")
        return user
        
    def regiser_user(self, new_user: User) -> User:
        exist = self.repo.get_user_by_email(new_user.email)
        if exist:
            raise ValueError("User already Exists.")
        self.repo.save_user(new_user)
        return new_user

    def delete_user(self, email: str) -> User:
        exist = self.repo.get_user_by_email(email)       
        if not exist:
            raise ValueError("User not Found.")
        self.repo.delete_user(exist)
        deleted_user = exist
        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        exist = self.repo.get_user_by_email(user_update.email)   
        if not exist:
            raise ValueError("User not Found")
        updated_user = exist
        return updated_user
        
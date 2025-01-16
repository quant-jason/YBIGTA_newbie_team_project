from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        ## TODO
        user = self.repo.get_user_by_email(user_login.email)
        print(user) # 지우기
        if user is None:
            raise ValueError("User not Found.")
        elif user.password != user_login.password:
            raise ValueError("Invalid ID/PW")
        else:
            return user
        
    def register_user(self, new_user: User) -> User:
        ## TODO
        input_email_check = self.repo.get_user_by_email(new_user.email)
        if input_email_check is not None:
            raise ValueError("User already Exists.")
        elif input_email_check is None:
            new = self.repo.save_user(new_user)
            print(new_user) # 지우기
            print(new) # 지우기
            return new

    def delete_user(self, email: str) -> User:
        ## TODO        
        email_check = self.repo.get_user_by_email(email)
        if email_check is None:
            raise ValueError("User not Found.")
        else:
            deleted_user = self.repo.delete_user(email_check)
            print(deleted_user) # 지우기
            return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        ## TODO
        email_check = self.repo.get_user_by_email(user_update.email)
        if email_check is None:
            raise ValueError("User not Found.")
        else:
            email_check.password = user_update.new_password
            self.repo.delete_user(email_check)
            updated_user = self.repo.save_user(email_check)
            return updated_user
        
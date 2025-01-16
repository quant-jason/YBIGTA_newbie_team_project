from fastapi import APIRouter, HTTPException, Depends, status
from app.user.user_schema import User, UserLogin, UserUpdate, UserDeleteRequest
from app.user.user_service import UserService
from app.dependencies import get_user_service
from app.responses.base_response import BaseResponse

user = APIRouter(prefix="/api/user")


@user.post("/login", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def login_user(user_login: UserLogin, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    try:
        user = service.login(user_login)
        return BaseResponse(status="success", data=user, message="Login Success.") 
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.post("/register", response_model=BaseResponse[User], status_code=status.HTTP_201_CREATED)
def register_user(user: User, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    """
    Register a new user.

    Args:
    - user (User): User type data for registration.
    - service (UserService): handling user-related services.

    Returns:
    BaseResponse[User]: Response with the registered user data and success message.

    Raises:
    HTTPException: If a user with the same email already exists.
    """
    try: 
        new_user = service.register_user(user)
        return BaseResponse(status="success", data=new_user, message="User registeration success.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@user.delete("/delete", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def delete_user(user_delete_request: UserDeleteRequest, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    """
    Delete an existing user by email.

    Args:
    - user_delete_request (UserDeleteRequest): request containing the email of the user to delete.
    - service (UserService): handling user-related services.

    Returns:
    - BaseResponse[User]: Response with the deleted user data and success message.

    Raises:
    HTTPException: If the user is not found.
    """
    try: 
        deleted_user = service.delete_user(user_delete_request.email)
        return BaseResponse(status="success", data=deleted_user, message="User Deletion Success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@user.put("/update-password", response_model=BaseResponse[User], status_code=status.HTTP_200_OK)
def update_user_password(user_update: UserUpdate, service: UserService = Depends(get_user_service)) -> BaseResponse[User]:
    ## TODO
    """
    Update the password of an existing user.

    Args:
    - user_update (UserUpdate): request containing the email and new password for the user.
    - service (UserService): handling user-related services.

    Returns:
    - BaseResponse[User]: Response with the updated user data and success message.

    Raises:
    - HTTPException: If the user is not found.
    """
    try: 
        updated_user = service.update_user_pwd(user_update)
        return BaseResponse(status="success", data=updated_user, message="User password update success.")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
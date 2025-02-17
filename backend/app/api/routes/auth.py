from fastapi import Request

from app.api_models.auth import RegisterRequest, RegisterResponse, UserResponse
from fastapi import APIRouter, Response, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, APIKeyHeader


import logging

from app.db_models.chats import User
from app.core.db import SessionLocal
from fastapi import HTTPException

from app.api.util import get_password_hash, verify_password, create_jwt, jwt_token_required

logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")
security_scheme = APIKeyHeader(name="Authorization", description="Bearer token")
auth_router = APIRouter()



@auth_router.post("/register")
def register(request: RegisterRequest) -> RegisterResponse:
    """
    :param request: The registration request object containing user details such as email, login, full name, password, address, birthday, and additional information.
    :return: The response object indicating successful registration or raises an HTTPException with appropriate error messages if registration fails.
    """
    with SessionLocal() as session:
        with session.begin():
            user = session.query(User).filter_by(email=request.email).first()
            if user:
                raise HTTPException(409, f'User with email {request.email} already exists')
            user = session.query(User).filter_by(login=request.login).first()
            if user:
                raise HTTPException(409, f'User with login {request.login} already exists')

            if len(request.fullName) > 255:
                raise HTTPException(400, f'Full name is too long')

            if len(request.password) < 8:
                raise HTTPException(400, f'Password is too short')

            user = User(name=request.fullName, email=request.email, password_hashed=get_password_hash(request.password),
                        login=request.login, address=request.address, birthday=request.birthday,
                        additional_info=request.additionalInfo)
            session.add(user)
            session.commit()

            return RegisterResponse()


@auth_router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None):
    """
    :param form_data: The form data containing the username and password of the user trying to log in.
    :type form_data: OAuth2PasswordRequestForm

    :param response: The response object used to set the HTTP cookie for the access token.
    :type response: Response

    :return: A dictionary containing the access token and the token type.
    :rtype: dict

    :raises HTTPException: If the user does not exist or the password is incorrect.
    """
    with SessionLocal() as session:
        with session.begin():
            user = session.query(User).filter_by(login=form_data.username).first()
            if not user:
                raise HTTPException(404, "User with credentials does not exist")

            if not verify_password(user.password_hashed, form_data.password):
                raise HTTPException(400, "Incorrect password")

            jwt_token = create_jwt(user.id)
            response.set_cookie(key="access_token", value=jwt_token, httponly=True)
            return {"access_token": jwt_token, "token_type": "bearer"}


@auth_router.get("/users/{user_id}", dependencies=[Depends(security_scheme)])
@jwt_token_required
def get_user(request: Request, user_id: int, user_payload=None) -> UserResponse:
    """
    :param request: The current request being processed.
    :param user_id: The unique identifier of the user to be retrieved.
    :param user_payload: The payload containing information about the user, typically extracted from the JWT token.
    :return: A UserResponse object containing the user's details if found, otherwise raises an HTTPException if the user is not found.
    """
    print(user_payload)
    with SessionLocal() as session:
        with session.begin():
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                raise HTTPException(404, f'User with id {user_id} does not exist')
            return UserResponse(id=user.id, fullName=user.name, email=user.email, address=user.address)

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_400_BAD_REQUEST
from src.core.services.user import UserService
from src.core.dbconfig.postgres import get_db
from src.core.models.base import User  # Make sure to import User model

accounts_router = APIRouter()

def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)

@accounts_router.post("/create")
async def create_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
    user_service: UserService = Depends(get_user_service)
):
    user_in = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
    )
    user = await user_service.create(user_in, password)
    return JSONResponse(
        status_code=200,
        content={"user_id": str(user.id), "email": user.email}
    )

@accounts_router.post("/signin")
async def authenticate_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service)
):
    is_authenticated = await user_service.login(form_data.username, form_data.password)
    if not is_authenticated:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password"
        )
    return JSONResponse(
        status_code=200,
        content={"message": "Login successful"}
    )


from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm



accounts_router = r = APIRouter()

@r.get("")
def get_current_user(
    
):
    """
    This is a test for a new endpoint
    """
    return JSONResponse(
        status_code=200,
        content={
            "username": "Byamasu Patrick",
            "email": "patrick@whatnow.is",
            "position": "AI Engineer"
        }
    )

@r.post("/signin")
def get_current_user(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    This is a test for a new endpoint
    """
    return JSONResponse(
        status_code=200,
        content={
            "username": form_data.username,
            "Password": form_data.password
        }
    )

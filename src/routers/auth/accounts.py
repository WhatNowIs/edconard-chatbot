from fastapi import APIRouter
from fastapi.responses import JSONResponse


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
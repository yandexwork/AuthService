from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from src.schemas.users import UserCreateForm
from src.services.users import UserService, get_user_service


router = APIRouter()


@router.post('/signup')
async def create_user(
        user_create_form: UserCreateForm,
        user_service: UserService = Depends(get_user_service)
):
    if not await user_service.is_user_exist(user_create_form):
        user = await user_service.create_user(user_create_form)
        return user
    return JSONResponse(
        content="Login is already taken",
        status_code=status.HTTP_502_BAD_GATEWAY
    )

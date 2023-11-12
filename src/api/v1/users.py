from http import HTTPStatus

from fastapi import APIRouter, Depends, Request

from src.models.users import User
from src.services.users import UserService, get_user_service
from src.services.auth import get_user_from_access_token

from src.schemas.users import UserCreateForm, ChangePasswordForm, FullUserSchema
from src.schemas.histories import LoginHistorySchema
from src.schemas.validators import Paginator
from src.limiter import limiter


router = APIRouter()


@router.post('/signup')
@limiter.limit("20/minute")
async def create_user(
        request: Request,
        user_create_form: UserCreateForm,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_create_form)


@router.put(
    '/change_password',
    status_code=HTTPStatus.NO_CONTENT
)
@limiter.limit("20/minute")
async def change_password(
        request: Request,
        change_password_form: ChangePasswordForm,
        user: User = Depends(get_user_from_access_token),
        user_service: UserService = Depends(get_user_service)
) -> None:
    await user_service.change_user_password(user, change_password_form)


@router.get(
    '/get_user_history',
    status_code=HTTPStatus.OK,
    response_model=list[LoginHistorySchema]
)
@limiter.limit("20/minute")
async def get_user_history(
        request: Request,
        paginator: Paginator = Depends(Paginator),
        user: User = Depends(get_user_from_access_token),
        user_service: UserService = Depends(get_user_service)
) -> list[LoginHistorySchema]:
    return await user_service.get_user_history(user, paginator)


@router.get(
    '/me',
    status_code=HTTPStatus.OK,
    response_model=FullUserSchema
)
@limiter.limit("20/minute")
async def get_user_info(
        request: Request,
        user: User = Depends(get_user_from_access_token),
        user_service: UserService = Depends(get_user_service)
) -> FullUserSchema:
    return await user_service.get_user_info(user)

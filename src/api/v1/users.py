from http import HTTPStatus

from fastapi import APIRouter, Depends

#models
from src.models.users import User
#schemas
from src.schemas.users import UserCreateForm, ChangePasswordForm, FullUserSchema
from src.schemas.histories import LoginHistorySchema
from src.schemas.validators import Paginator
#services
from src.services.users import UserService, get_user_service
from src.services.auth import user_from_access


router = APIRouter()


@router.post('/signup')
async def create_user(
        user_create_form: UserCreateForm,
        user_service: UserService = Depends(get_user_service)
):
    return await user_service.create_user(user_create_form)


@router.put(
    '/change-password',
    status_code=HTTPStatus.NO_CONTENT
)
async def change_password(
        change_password_form: ChangePasswordForm,
        user: User = Depends(user_from_access),
        user_service: UserService = Depends(get_user_service)
) -> None:
    await user_service.change_user_password(user, change_password_form)


@router.get(
    '/get-user-history',
    status_code=HTTPStatus.OK,
    response_model=list[LoginHistorySchema]
)
async def get_user_history(
        paginator: Paginator = Depends(Paginator),
        user: User = Depends(user_from_access),
        user_service: UserService = Depends(get_user_service)
) -> list[LoginHistorySchema]:
    return await user_service.get_user_history(user, paginator)


@router.get(
    '/me',
    status_code=HTTPStatus.OK,
    response_model=FullUserSchema
)
async def get_user_info(
        user: User = Depends(user_from_access),
        user_service: UserService = Depends(get_user_service)
) -> FullUserSchema:
    return await user_service.get_user_info(user)

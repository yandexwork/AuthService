from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.models.users import User
from src.models.roles import Role

from src.schemas.validators import Paginator
from src.schemas.roles import RoleCreateForm, RoleSchema, RoleAttachForm, RoleUpdateForm

from src.services.auth import get_user_from_access_token
from src.services.roles import RolesService, get_role_service

from src.core.exceptions import USER_DOES_NOT_HAVE_RIGHTS


router = APIRouter()


@router.get('/', status_code=HTTPStatus.OK, response_model=list[RoleSchema])
async def get_roles(
        paginator: Paginator = Depends(Paginator),
        role_service: RolesService = Depends(get_role_service)
) -> list[RoleSchema]:
    return await role_service.get_roles(paginator)


@router.post('/', status_code=HTTPStatus.CREATED, response_model=RoleSchema)
async def create_role(
        role_create_form: RoleCreateForm,
        user: User = Depends(get_user_from_access_token),
        role_service: RolesService = Depends(get_role_service)
) -> Role:
    if user.is_admin():
        return await role_service.create_role(role_create_form)
    raise USER_DOES_NOT_HAVE_RIGHTS


@router.delete('/{role_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete_role(
        role_id: UUID,
        user: User = Depends(get_user_from_access_token),
        role_service: RolesService = Depends(get_role_service)
) -> None:
    if user.is_admin():
        return await role_service.delete_role(role_id)
    raise USER_DOES_NOT_HAVE_RIGHTS


@router.put('/{role_id}', response_model=RoleSchema, status_code=HTTPStatus.OK)
async def update_role(
        role_id: UUID,
        role_update_form: RoleUpdateForm,
        user: User = Depends(get_user_from_access_token),
        role_service: RolesService = Depends(get_role_service)
) -> RoleSchema:
    if user.is_admin():
        return await role_service.update_role(role_id, role_update_form)
    raise USER_DOES_NOT_HAVE_RIGHTS


@router.post('/attach_role', status_code=HTTPStatus.NO_CONTENT)
async def attach_role(
        role_attach_form: RoleAttachForm,
        user: User = Depends(get_user_from_access_token),
        role_service: RolesService = Depends(get_role_service)
) -> None:
    if user.is_admin():
        return await role_service.attach_role(role_attach_form)
    raise USER_DOES_NOT_HAVE_RIGHTS


@router.delete('/detach_role/', status_code=HTTPStatus.NO_CONTENT)
async def detach_role(
        user_id: UUID = Query(),
        role_id: UUID = Query(),
        user: User = Depends(get_user_from_access_token),
        role_service: RolesService = Depends(get_role_service)
) -> None:
    if user.is_admin():
        role_attach_form = RoleAttachForm(user_id=user_id, role_id=role_id)
        return await role_service.detach_role(role_attach_form)
    raise USER_DOES_NOT_HAVE_RIGHTS

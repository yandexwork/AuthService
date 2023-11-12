from http import HTTPStatus

from fastapi import APIRouter, Response, Request, Depends

from src.models.users import User
from src.schemas.tokens import Tokens, AccessToken
from src.schemas.users import UserLoginForm

from src.services.auth import get_user_from_access_token, get_user_from_refresh_token
from src.services.tokens import TokenService, get_token_service
from src.limiter import limiter


router = APIRouter()


@router.post('/login',
             response_model=Tokens,
             status_code=HTTPStatus.OK)
@limiter.limit("20/minute")
async def get_tokens(
        payload: UserLoginForm,
        response: Response,
        request: Request,
        token_service: TokenService = Depends(get_token_service)
) -> Tokens:
    """Вход пользователя в систему"""
    return await token_service.login(payload.login, payload.password,
                                     request, response)


@router.post('/login/google',
             response_model=Tokens,
             status_code=HTTPStatus.OK)
@limiter.limit("20/minute")
async def get_google_tokens(
        response: Response,
        request: Request,
        token_service: TokenService = Depends(get_token_service)
) -> Tokens:
    return await token_service.google_login(request, response)


@router.post(
    '/refresh',
    response_model=AccessToken,
    status_code=HTTPStatus.OK
)
@limiter.limit("20/minute")
async def refresh_access_token(
        response: Response,
        request: Request,
        user: User = Depends(get_user_from_refresh_token),
        token_service: TokenService = Depends(get_token_service)
) -> AccessToken:
    """Обновление access токена"""
    return await token_service.refresh(user, request, response)


@router.get(
    '/logout',
    status_code=HTTPStatus.NO_CONTENT
)
@limiter.limit("20/minute")
async def logout_from_all_devices(
        request: Request,
        user: User = Depends(get_user_from_access_token),
        token_service: TokenService = Depends(get_token_service)
) -> None:
    """Выход из аккаунта со всех устройств"""
    await token_service.logout(user.id)


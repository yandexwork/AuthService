from datetime import timedelta, datetime
from functools import lru_cache
from http import HTTPStatus
from uuid import UUID
from logging import Logger

from async_fastapi_jwt_auth import AuthJWT
from async_fastapi_jwt_auth.exceptions import MissingTokenError, JWTDecodeError
from fastapi import Depends, Response, Request
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from werkzeug.security import generate_password_hash

from src.core.exceptions import CustomException, ErrorMessagesUtil
from src.core.config import settings, auth_jwt_settings
from src.db.postgres import get_session
from src.db.redis import get_redis
from src.models.history import LoginHistory
from src.models.tokens import RefreshTokens
from src.models.users import User
from src.schemas.tokens import Tokens, AccessToken


async def user_from_access(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        authorize: AuthJWT = Depends()
) -> User:
    try:
        await authorize.jwt_required()
    except (MissingTokenError, JWTDecodeError):
        raise CustomException(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ErrorMessagesUtil.user_not_authorized()
        )

    user_id = await authorize.get_jwt_subject()
    data = await db.execute(select(User).where(User.id == user_id))
    user: User = data.scalar()

    logout_time = await redis.get(str(user.id))
    if logout_time:
        token = await authorize.get_raw_jwt()
        created_at = token['iat']
        if created_at <= float(logout_time.decode()):
            await authorize.unset_jwt_cookies()
            raise CustomException(
                status_code=HTTPStatus.BAD_REQUEST,
                message=ErrorMessagesUtil.access_token_is_invalid()
            )

    return user


async def user_from_refresh(
        db: AsyncSession = Depends(get_session),
        authorize: AuthJWT = Depends()
) -> User:
    try:
        await authorize.jwt_refresh_token_required()
    except (MissingTokenError, JWTDecodeError):
        raise CustomException(
            status_code=HTTPStatus.UNAUTHORIZED,
            message=ErrorMessagesUtil.user_not_authorized()
        )

    user_id = await authorize.get_jwt_subject()
    if not user_id:
        raise CustomException(
            status_code=HTTPStatus.CONFLICT,
            message=ErrorMessagesUtil.unable_to_refresh_token()
        )

    sql_request = await db.execute(select(User).where(User.id == user_id))
    user = sql_request.scalar()
    if not user:
        raise CustomException(
            status_code=HTTPStatus.CONFLICT,
            message=ErrorMessagesUtil.user_not_found()
        )

    return user


class TokenService:
    def __init__(self, db: AsyncSession, redis: Redis,
                 authorize: AuthJWT, logger: Logger):
        self.db = db
        self.redis = redis
        self.authorize = authorize
        self.logger = logger

    async def get_user_by_login(self, login: str) -> User:
        sql_request = await self.db.execute(select(User).where(User.login == login))
        user: User = sql_request.scalar()
        if not user:
            raise CustomException(
                status_code=HTTPStatus.BAD_REQUEST, message=ErrorMessagesUtil.user_not_found()
            )
        self.logger.debug(f'Get user by login - input: [login: {login}]; output: [user_id: {user.id}];')
        return user

    async def login(self, login: str, password: str, request: Request, response: Response) -> Tokens:
        user = await self.get_user_by_login(login)

        if not user.check_password(password):
            raise CustomException(
                status_code=HTTPStatus.BAD_REQUEST, message=ErrorMessagesUtil.wrong_password()
            )

        tokens = await self.create_tokens(user.id)
        await self.save_refresh_token(user.id, tokens.refresh_token)
        await self.save_entry_information(user.id, request.headers['user-agent'])
        await self.set_tokens_to_cookie(response, tokens)

        self.logger.debug(f'Login - input: [login: {login},'
                          f'password: {generate_password_hash(password)}]; '
                          f'output: [tokens: {tokens}];')
        return tokens

    async def refresh(self, user: User, request: Request, response: Response):
        refresh_token_cookie = request.cookies[auth_jwt_settings.authjwt_refresh_cookie_key]

        if await self.is_refresh_token_exist(user.id, refresh_token_cookie):
            access_token = await self.create_access_token(user.id)
            await self.set_access_token_to_cookie(response, access_token.access_token)
            self.logger.debug(f'Refresh - input: [user_id: {user.id}]; '
                              f'output: [access_token: {access_token}];')
            return access_token

        raise CustomException(
            status_code=HTTPStatus.BAD_REQUEST,
            message=ErrorMessagesUtil.refresh_token_is_invalid()
        )

    async def create_access_token(self, user_id: UUID) -> AccessToken:
        access_token = await self.authorize.create_access_token(
            subject=str(user_id),
            expires_time=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
        )
        self.logger.debug(f'Create access token - input: [user_id: {user_id}]; '
                          f'output: [access_token: {access_token}];')
        return AccessToken(access_token=access_token)

    async def create_tokens(self, user_id: UUID) -> Tokens:

        access_token = await self.create_access_token(user_id)

        refresh_token = await self.authorize.create_refresh_token(
            subject=str(user_id),
            expires_time=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE)
        )

        self.logger.debug(f'Create tokens - input: [user_id: {user_id}]; '
                          f'output: [access_token: {access_token}, '
                          f'refresh_token: {refresh_token}];')
        return Tokens(
            access_token=access_token.access_token,
            refresh_token=refresh_token
        )

    async def save_refresh_token(self, user_id: UUID, refresh_token: str) -> None:
        refresh_token_entry = RefreshTokens(
            user_id=user_id,
            refresh_token=refresh_token
        )
        self.logger.debug(f'Save refresh token - input: [user_id: {user_id}, '
                          f'refresh_token: {refresh_token}];')
        self.db.add(refresh_token_entry)
        await self.db.commit()

    async def save_entry_information(self, user_id: UUID, user_agent: str) -> None:
        login_history = LoginHistory(
            user_id=user_id,
            user_agent=user_agent
        )
        self.logger.debug(f'Save entry information - input: [user_id: {user_id}, '
                          f'user_agent: {user_agent}];')
        self.db.add(login_history)
        await self.db.commit()

    @staticmethod
    async def set_access_token_to_cookie(response: Response, access_token: str) -> None:
        response.set_cookie('access_token', access_token,
                            settings.ACCESS_TOKEN_EXPIRE,
                            settings.ACCESS_TOKEN_EXPIRE,
                            '/', None, False, True, 'lax')

    async def set_tokens_to_cookie(self, response: Response, tokens: Tokens) -> None:
        await self.set_access_token_to_cookie(response, tokens.access_token)
        response.set_cookie('refresh_token', tokens.refresh_token,
                            settings.REFRESH_TOKEN_EXPIRE,
                            settings.REFRESH_TOKEN_EXPIRE,
                            '/', None, False, True, 'lax')

    async def is_refresh_token_exist(self, user_id: UUID, refresh_token: str) -> bool:
        sql_request = await self.db.execute(
            select(RefreshTokens).where(
                RefreshTokens.user_id == user_id
            ).filter(RefreshTokens.refresh_token == refresh_token))
        refresh_token_in_db = sql_request.scalar()
        self.logger.debug(f'Is refresh token exist - input: ['
                          f'user_id: {user_id}, refresh_token: {refresh_token}]; '
                          f'output: [flag: {bool(refresh_token_in_db)}];')

        if not refresh_token_in_db:
            return False
        return True

    async def logout(self, user_id: UUID) -> None:
        await self.db.execute(delete(RefreshTokens).where(RefreshTokens.user_id == user_id))
        await self.db.commit()
        date = datetime.utcnow()
        await self.redis.set(str(user_id), str(date.timestamp()), settings.ACCESS_TOKEN_EXPIRE)
        await self.authorize.unset_jwt_cookies()


@lru_cache()
def get_token_service(
        db: AsyncSession = Depends(get_session),
        redis: Redis = Depends(get_redis),
        authorize: AuthJWT = Depends(),
) -> TokenService:
    return TokenService(db, redis, authorize, logger)
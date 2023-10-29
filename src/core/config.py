from async_fastapi_jwt_auth import AuthJWT
from pydantic_settings import BaseSettings


class AuthJWTSettings(BaseSettings):
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_token_location: set = {"cookies", "headers"}
    authjwt_secret_key: str = 'some_key'


class Setting(BaseSettings):
    DB_URL: str


@AuthJWT.load_config
def get_auth_settings() -> AuthJWTSettings:
    return AuthJWTSettings()


settings = Setting()
auth_jwt_settings = AuthJWTSettings()

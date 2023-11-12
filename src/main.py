from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware

from src.core.exceptions import CustomException
from src.services.users import create_admin
from src.limiter import limiter
from src.api.v1 import users
from src.api.v1 import auth
from src.api.v1 import roles
from src.core.config import auth_jwt_settings


app = FastAPI(
    title='AuthService',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SessionMiddleware, secret_key=auth_jwt_settings.authjwt_secret_key)


@app.exception_handler(CustomException)
async def uvicorn_exception_handler(request: Request, exc: CustomException):
    return ORJSONResponse(status_code=exc.status_code, content={'message': exc.message})


@app.on_event("startup")
async def startup() -> None:
    await create_admin()


app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])
app.include_router(roles.router, prefix='/api/v1/roles', tags=['roles'])

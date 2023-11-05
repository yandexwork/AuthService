from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

from src.core.exceptions import CustomException
from src.api.v1 import users
from src.api.v1 import auth


app = FastAPI(
    title='AuthService',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)


@app.exception_handler(CustomException)
async def uvicorn_exception_handler(request: Request, exc: CustomException):
    return ORJSONResponse(status_code=exc.status_code, content={'message': exc.message})


app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(auth.router, prefix='/api/v1/auth', tags=['auth'])

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from src.api.v1 import users


app = FastAPI(
    title='AuthService',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)


app.include_router(users.router, prefix='/api/v1/users', tags=['users'])

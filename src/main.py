import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import users
from db.postgres import create_database


app = FastAPI(
    title='AuthService',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse
)

# @app.on_event('startup')
# async def startup():
#     # from models.entity import User
#     await create_database()


app.include_router(users.router, prefix='/api/v1/users', tags=['users'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
    )

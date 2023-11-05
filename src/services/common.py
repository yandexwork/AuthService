from async_fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio.client import Redis


class BaseService:

    def __init__(
            self, db: AsyncSession,
            redis: Redis = None,
            authorize: AuthJWT = None):
        self.db = db
        self.redis = redis
        self.authorize = authorize

    async def update_model_object(self, model_object) -> None:
        self.db.add(model_object)
        await self.db.commit()
        await self.db.refresh(model_object)

from functools import lru_cache
from typing import Optional

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.users import UserCreateForm
from src.models.users import User
from src.db.postgres import get_session


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_login(self, login: str) -> Optional[User]:
        query = await self.db.execute(select(User).where(User.login == login))
        user = query.first()
        return user

    async def is_user_exist(self, user_create_form: UserCreateForm) -> bool:
        return True if await self.get_user_by_login(user_create_form.login) else False

    async def create_user(self, user_create_form: UserCreateForm) -> User:
        user_dto = jsonable_encoder(user_create_form)
        user = User(**user_dto)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


@lru_cache()
def get_user_service(
        db: AsyncSession = Depends(get_session)
) -> UserService:
    return UserService(db)

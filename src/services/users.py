from functools import lru_cache
from http import HTTPStatus
from uuid import UUID

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from src.core.exceptions import CustomException, ErrorMessagesUtil
from src.schemas.users import UserCreateForm, ChangePasswordForm, FullUserSchema
from src.schemas.histories import LoginHistorySchema
from src.schemas.validators import Paginator
from src.models.users import User
from src.models.history import LoginHistory
from src.db.postgres import get_session


class UserService:
    user_already_exist_exception = CustomException(
        status_code=HTTPStatus.CONFLICT,
        message=ErrorMessagesUtil.user_already_exists()
    )

    wrong_password_exception = CustomException(
        status_code=HTTPStatus.BAD_REQUEST,
        message=ErrorMessagesUtil.wrong_password()
    )

    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_user(self, user: User) -> None:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

    async def create_user(self, user_create_form: UserCreateForm) -> User:
        try:
            # DTO - data transfer object
            user_dto = jsonable_encoder(user_create_form)
            user = User(**user_dto)
            await self.update_user(user)
            return user
        except IntegrityError:
            raise self.user_already_exist_exception

    async def change_user_password(
            self, user: User, change_password_form: ChangePasswordForm
    ) -> None:
        if not user.check_password(change_password_form.previous_password):
            raise self.wrong_password_exception
        user.password = generate_password_hash(change_password_form.new_password)
        await self.update_user(user)

    async def get_login_history_query(
            self, user_id: UUID, page_number: int, page_size: int
    ) -> Result:
        query = await self.db.execute(
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id)
            .order_by(LoginHistory.created_at.desc())
            .offset((page_number - 1) * page_size)
            .limit(page_size)
        )
        return query

    @staticmethod
    def get_login_records_from_query(query: Result) -> list[LoginHistorySchema]:
        login_records = [login_record for login_record in query.scalars().all()]
        return login_records

    async def get_user_history(self, user: User, paginator: Paginator) -> list[LoginHistorySchema]:
        query = await self.get_login_history_query(user.id, paginator.page_number, paginator.page_size)
        login_records = self.get_login_records_from_query(query)
        return login_records

    @staticmethod
    async def get_user_info(user: User) -> FullUserSchema:
        # DTO - data transfer object
        user_dto = jsonable_encoder(user)
        return FullUserSchema(**user_dto)


@lru_cache()
def get_user_service(
        db: AsyncSession = Depends(get_session)
) -> UserService:
    return UserService(db)

from uuid import UUID

from pydantic import BaseModel


class UserCreate(BaseModel):
    login: str = 'testuser'
    password: str = 'qwerty12345'
    first_name: str = 'bob'
    last_name: str = 'smith'


class UserInDB(BaseModel):
    id: UUID
    first_name: str
    last_name: str

    class Config:
        orm_mode = True
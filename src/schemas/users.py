from pydantic import BaseModel, validator


class UserCreateForm(BaseModel):
    login: str = 'testuser'
    password: str = 'qwerty12345'
    first_name: str = 'bob'
    last_name: str = 'smith'

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        return v

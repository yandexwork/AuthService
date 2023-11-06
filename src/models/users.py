import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src.db.postgres import Base
from src.models.roles import Role


UserRoles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', ForeignKey('users.id')),
    Column('role_id', ForeignKey('roles.id'))
)


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    roles = relationship(Role, secondary=UserRoles, backref='users', lazy='selectin')
    created_at = Column(DateTime, default=datetime.utcnow)

    def __init__(self, login: str, password: str, first_name: str, last_name: str) -> None:
        self.login = login
        self.password = self.password = generate_password_hash(password)
        self.first_name = first_name
        self.last_name = last_name

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def is_admin(self):
        for role in self.roles:
            if role.name == 'admin':
                return True
        return False

    def __repr__(self) -> str:
        return f'<User {self.login}>'

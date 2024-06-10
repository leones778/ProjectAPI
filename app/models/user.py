from datetime import UTC, date, datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import ENUM as EnumPostgres
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.utils import uuidhex
from app.models.base import Base


class Role(Enum):
    ADMIN = "admin"
    WORKER = "worker"


class LoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterSchema(LoginSchema):
    first_name: str
    last_name: str
    middle_name: str | None = None


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(default=uuidhex, primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    middle_name: Mapped[str | None] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    created_at: Mapped[date] = mapped_column(default=date.today)
    role: Mapped[Role] = mapped_column(EnumPostgres(Role, name="role_enum"))

    session: Mapped["UserSession"] = relationship("UserSession", back_populates="user")

    def to_dict(self):
        return {
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "middle_name": self.middle_name,
            "created_at": self.created_at.isoformat(),
            "role": self.role.value,
        }


class UserSession(Base):
    __tablename__ = "user_sessions"

    session_id: Mapped[str] = mapped_column(default=uuidhex, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"))
    user: Mapped["User"] = relationship("User", back_populates="session")

    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    expiration_at: Mapped[datetime] = mapped_column()

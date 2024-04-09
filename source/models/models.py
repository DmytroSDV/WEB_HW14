import enum
from datetime import date

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Enum, Boolean
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    ...

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    second_name: Mapped[str] = mapped_column(String(50), index=True)
    email_add: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    phone_num: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    birth_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[date] = mapped_column("crated_at", DateTime, default=func.now(),nullable=True)
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, 
                                             default=func.now(), onupdate=func.now(), nullable=True)

    consumer_id: Mapped[int] = mapped_column(Integer, ForeignKey('consumers.id'), nullable=True)
    consumer: Mapped["Consumer"] = relationship("Consumer", backref="users", lazy="joined")

class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"

class Consumer(Base):
    __tablename__ = 'consumers'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[date] = mapped_column('created_at', DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column('updated_at', DateTime, default=func.now(), onupdate=func.now())
    role: Mapped[Enum] = mapped_column('role', Enum(Role), default=Role.user, nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)


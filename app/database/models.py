from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from config import DATABASE

engine = create_async_engine(url=DATABASE)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    """Таблица пользователей."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_interaction: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    is_courier: Mapped[bool] = mapped_column(Boolean, default=False)
    has_business: Mapped[bool] = mapped_column(Boolean, default=False)
    business: Mapped[Optional["Business"]] = relationship(
        "Business", back_populates="user", uselist=False
    )
    courier: Mapped[Optional["Courier"]] = relationship(
        "Courier", back_populates="user", uselist=False
    )


class Business(Base):
    """Таблица бизнесов."""

    __tablename__ = "businesses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_name: Mapped[str] = mapped_column(String(64), index=True)
    address: Mapped[str] = mapped_column(String(128))
    coordinates: Mapped[str] = mapped_column(String(64), nullable=True)
    contact_person: Mapped[str] = mapped_column(String(64))
    contact_phone: Mapped[str] = mapped_column(String(64))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship("User", back_populates="business")
    deliveries: Mapped[list["Delivery"]] = relationship(
        "Delivery", back_populates="business"
    )


class Courier(Base):
    """Таблица курьеров."""

    __tablename__ = "couriers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    courier_name: Mapped[str] = mapped_column(String(64), index=True)
    contact_phone: Mapped[str] = mapped_column(String(32))
    photo_url: Mapped[str] = mapped_column(String(64), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship("User", back_populates="courier")
    deliveries: Mapped[list["Delivery"]] = relationship(
        "Delivery", back_populates="courier"
    )


class Delivery(Base):
    """Таблица быстрых доставок."""

    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    start_geo: Mapped[str] = mapped_column(String(128), index=True)
    end_geo: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str] = mapped_column(String(32))
    client_phone: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(32), default="В ожидании")
    price: Mapped[int] = mapped_column(Integer())
    yandex_url: Mapped[str] = mapped_column(String(128))
    message_id: Mapped[int] = mapped_column(Integer())
    chat_id: Mapped[int] = mapped_column(Integer())
    courier_id: Mapped[int] = mapped_column(ForeignKey("couriers.id"), nullable=True)
    courier: Mapped[Courier] = relationship("Courier", back_populates="deliveries")
    business_id: Mapped[int] = mapped_column(ForeignKey("businesses.id"), nullable=True)
    business: Mapped[Business] = relationship("Business", back_populates="deliveries")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

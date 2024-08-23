from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from config import DATABASE

engine = create_async_engine(url=DATABASE)

async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    last_interaction: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Business(Base):
    __tablename__ = 'businesses'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    business_name: Mapped[str] = mapped_column(String(256), index=True)
    address: Mapped[str] = mapped_column(String(256))
    contact_person: Mapped[str] = mapped_column(String(256))
    contact_phone: Mapped[str] = mapped_column(String(256))
    

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
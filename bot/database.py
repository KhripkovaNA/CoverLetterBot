from datetime import datetime
from bot.config import database_url
from sqlalchemy import func, TIMESTAMP, Integer
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession

# Create the asynchronous engine using the database URL from the config
engine = create_async_engine(url=database_url)

# Create an asynchronous session maker, which will be used for managing sessions
async_session_maker = async_sessionmaker(engine, class_=AsyncSession)


# Decorator automatically creates and handles the session for database operations
def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)  # Pass session to the decorated method
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    return wrapper


# Abstract base class for all database models
class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now()
    )

    @classmethod
    @property
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + 's'


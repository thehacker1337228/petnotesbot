from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from config import DB_URL
import time


#engine = create_async_engine("sqlite+aiosqlite:///data/pet_notes_database.db")
engine = create_async_engine(DB_URL)
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'Users'

    user_id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    tg_id = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[int] = mapped_column(nullable=True)
    state: Mapped[str] = mapped_column(nullable=True)
    json_data: Mapped[str] = mapped_column(nullable=True)

class Note(Base):
    __tablename__ = 'Notes'

    note_id: Mapped[int] = mapped_column(primary_key = True, autoincrement = True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('Users.tg_id', ondelete="RESTRICT"))
    title: Mapped[str] = mapped_column(String(4096), nullable=True)
    content: Mapped[str] = mapped_column(String(4096), nullable=True)
    created_at: Mapped[int] = mapped_column(nullable=True, default=lambda: round(time.time()))
    updated_at: Mapped[int] = mapped_column(nullable=True)
    is_deleted: Mapped[int] = mapped_column(nullable=True)



async def init_main(): #функция создающая все эти таблицы если их не существует
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


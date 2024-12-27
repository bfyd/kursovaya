from sqlalchemy import BigInteger, String, ForeignKey,Boolean, Integer,Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass

class del_last_mes(Base):
    __tablename__ = 'del_last_mess'
    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id = mapped_column(BigInteger)
    mes_id = mapped_column(BigInteger)
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id= mapped_column(BigInteger)
    admin = mapped_column(Boolean)
    link = mapped_column(String)
    premium = mapped_column(Boolean)
    mes_id = mapped_column(BigInteger)
    mez = mapped_column(Text)

class Link(Base):
    __tablename__ = 'links'

    id: Mapped[int] = mapped_column(primary_key=True)
    name = mapped_column(String)
    new_members = mapped_column(Integer)

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
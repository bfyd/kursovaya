from database.models import async_session
from database.models import User,Link,del_last_mes
from sqlalchemy import select,update, delete,desc,func

async def set_user(tg_id,link,premium):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id,link = link,premium = premium))
            await session.commit()

async def set_maze(tg_id,maze):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            matrix_rows = '\n'.join([' '.join(row) for row in maze])
            user.mez = matrix_rows
            await session.commit()

async def get_maze(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            loaded_data = user.mez
            return loaded_data
async def add_game(tg_id,mes_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        user.mes_id = mes_id
        await session.commit()
async def del_game(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        user.mes_id = None
        await session.commit()
async def get_game(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        return user
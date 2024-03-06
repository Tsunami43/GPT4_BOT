from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import ChatTypeFilter, CommandStart, Command
from aiogram.types import ChatType
from asyncpg import Pool

from loader import dp


@dp.message_handler(Command("my_profile"), ChatTypeFilter([ChatType.PRIVATE]), state= '*')
async def my_profile(message: types.Message, state : FSMContext, pool : Pool):
    async with pool.acquire() as con:
        user = await con.fetchrow(f'''select * from users where user_id = {message.from_user.id}''')
    await message.answer(f'''
Количество использований

Текст: {user['num_of_tries_text']}''')
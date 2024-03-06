import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, ChatTypeFilter
from aiogram.types import ChatType, MediaGroup
from asyncpg import UniqueViolationError, Pool

from loader import dp
from states.generation_states import GenerateText


@dp.message_handler(CommandStart(), ChatTypeFilter([ChatType.PRIVATE]), state= '*')
async def bot_start(message: types.Message, state : FSMContext, pool : Pool, is_subscribed : bool):
    await state.reset_state()

    async with pool.acquire() as con:
        try:
            args = message.get_args()
            await con.execute(f'''insert into users(user_id, username, first_name, full_name, deeplink, datetime) values
            ({message.from_user.id}, '{message.from_user.username}', '{message.from_user.first_name.replace("'", "''")}',
            '{message.from_user.full_name.replace("'", "''")}',  '{args if args else None}', '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp)
            ON conflict(user_id) do nothing'''.replace("'None'", "null"))
        except UniqueViolationError:
            pass

    #await GenerateText.S1.set()
    text = f'''
Вы подписались на GPT4_Kolersky! Он использует самую крутую и современную мультимодальную нейросеть ChatGPT-4

Подпишитесь на канал, чтобы всегда иметь актуальную информацию: @kolerskych
Там же обсуждение и вопросы.
<a href="https://kolersky.com/botgpt4">Инструкция к прочтению</a>

Так же есть боты: 
@Dalle_Kolersky_Bot
@GPT_Kolersky_bot
'''

    await message.answer(text, disable_web_page_preview=True)
    if not is_subscribed:
        await asyncio.sleep(1)
        await message.answer(f'''Для использования нейросети оплатите доступ. После этого вы сразу сможете пользоваться нейросетью.
Нажмите /vip''')


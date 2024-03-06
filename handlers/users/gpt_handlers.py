import html
import logging

import aiohttp
import asyncpg
from aiogram.dispatcher.filters import ChatTypeFilter, Command
from aiogram.types import Message, ChatType, ChatActions, ContentTypes
#from async_openai import CompletionResponse, OpenAI
from aiohttp import ContentTypeError
from asyncpg import Pool

from loader import dp, openai_headers, admins, exceptions_chat_id
from states.generation_states import GenerateText, GenerateImage


# @dp.message_handler(Command("text"), ChatTypeFilter([ChatType.PRIVATE]),state='*')
# async def set_generate_text_state(message: Message):
#     await GenerateText.S1.set()
#     await message.answer("Вы перешли в режим генерации текста")
#
# @dp.message_handler(Command("photo"), ChatTypeFilter([ChatType.PRIVATE]),state='*')
# async def set_generate_text_state(message: Message):
#     await GenerateImage.Image_512.set()
#     await message.answer("Вы перешли в режим генерации фото")
from utils.dop_functions import split_text_every_n_symbols


@dp.message_handler(ChatTypeFilter([ChatType.PRIVATE]), content_types=ContentTypes.PHOTO, state= "*")
async def generate_text(message: Message):
    await message.answer(f'''В данный момент OpenAI не открыли доступ к обработке изображений, ожидаем анонса.''')


@dp.message_handler(ChatTypeFilter([ChatType.PRIVATE]), content_types=ContentTypes.TEXT,  state= "*")
async def generate_text(message: Message, pool : Pool):
    if len(message.text)>1500:
        await message.reply(f"Лимит ограничения символов - 1500, в вашем тексте: {len(message.text)} символов")
        return

    async with pool.acquire() as con:
        try:
            await con.fetchval(f'''update users set num_of_tries_text = num_of_tries_text - 1 where user_id = {message.from_user.id}''')
        except asyncpg.exceptions.CheckViolationError:
            await message.answer("У вас закончились попытки генерации текста, купить можно по команде /vip")
            return

        async with aiohttp.ClientSession() as session:
            await message.answer_chat_action(action=ChatActions.TYPING)
            resp = await session.post(url="https://api.openai.com/v1/chat/completions", headers=openai_headers,
                                  json={"model": "gpt-4-vision-preview",
                                        "max_tokens": 1000,
                                        "messages": [{"role":"user", "content" : message.text} ] #{"role":"system", "content" : ""}
                                        })
            try:
                data_resp = await resp.json()
                if data_resp.get('error'):
                    text = data_resp['error']['message'] #(await translator.translate(data_resp['error']['message'], "ru"))
                    await con.fetchval(f'''update users set num_of_tries_text = num_of_tries_text + 1 where user_id = {message.from_user.id}''')
                    await message.answer(text)
                    return
                text_of_response : str = data_resp['choices'][0]['message']['content']
            except (KeyError, ContentTypeError) as exc:
                await con.fetchval(f'''update users set num_of_tries_text = num_of_tries_text + 1 where user_id = {message.from_user.id}''')
                await message.reply("Во время обработки вашего запроса случилась непредвиденная ошибка")
                await dp.bot.send_message(chat_id=exceptions_chat_id,text=f"Ошибка: {html.escape(exc.__str__())}\n\nТекст запроса: {html.escape(await resp.text())}")
                logging.exception(f"Ошибка: {exc}\n\nТекст запроса: {resp.text()}")
                return

            try:
                if len(text_of_response)>4000:
                    for part_of_text in split_text_every_n_symbols(text_of_response):
                        await message.answer(part_of_text)
                else:
                    await message.answer(text=html.escape(text_of_response))
            except Exception as exc:
                logging.exception(f"Ошибка: {exc}\n\nТекст запроса: {resp.text()}")
                await con.fetchval(f'''update users set num_of_tries_text = num_of_tries_text + 1 where user_id = {message.from_user.id}''')






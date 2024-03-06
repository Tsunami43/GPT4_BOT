from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentTypes, Message
from asyncpg import Pool

from keyboards.default.admin import admin_menu_kb, cancel_kb, send_kb
from loader import bot, dp, admins


class Mailing(StatesGroup):
    get_message = State()
    get_ready = State()
    get_wait = State()

@dp.message_handler(user_id = admins,commands=['admin'], state='*')
async def admin_menu_command(message: types.Message, state : FSMContext):
    await state.reset_state()
    await bot.send_message(message.from_user.id, "Добро пожаловать в админ панель!", reply_markup=admin_menu_kb)

@dp.message_handler(user_id = admins, content_types=['text'], text='Рассылка')
async def mailing_handler(message: types.Message):
    await Mailing.get_message.set()
    await message.reply("Введите текст рассылки", reply_markup=cancel_kb)

@dp.message_handler(user_id = admins, content_types=[types.ContentType.ANY], state=Mailing.get_message)
async def get_text_mailing(message: types.Message, state: FSMContext):
    text = message.text
    if text == "Назад":
        await state.finish()
        await bot.send_message(message.from_user.id, "Добро пожаловать в админ панель!", reply_markup=admin_menu_kb)
    else:
        await state.update_data(message_id=message.message_id)
        await Mailing.get_ready.set()
        msg = await bot.copy_message(message.from_user.id, message.from_user.id, message.message_id)
        await bot.send_message(message.from_user.id, "Если сообщение которое вы хотите разослать это, то нажмите на кнопку Отправить!",
                               reply_markup=send_kb, reply_to_message_id=msg.message_id)

@dp.message_handler(user_id = admins, state=Mailing.get_ready)
async def get_mailing_ready(message: types.Message, state: FSMContext, pool : Pool):
    text = message.text
    data = await state.get_data()

    async with pool.acquire() as con:
        get_all_users = await con.fetch(f'''select * from users''')

    if text == 'Отправить':
        success = 0
        fail = 0
        await message.reply("Рассылка началась!", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
        for user_info in get_all_users:
            try:
                await bot.copy_message(user_info['user_id'], message.from_user.id, data['message_id'])
                success += 1
            except:
                fail += 1

        await message.reply("Рассылка завершена!\n"
                            f"Успешно: {success}\n"
                            f"Заблокировано: {fail}", reply_markup=admin_menu_kb)
    elif text == 'Назад':
        await Mailing.get_message.set()
        await message.reply("Введите текст рассылки", reply_markup=cancel_kb)


@dp.message_handler(content_types=ContentTypes.PHOTO, user_id = admins, state = '*')
async def get_photo_id(message : Message):
    await message.reply(text=message.photo[-1].file_id)


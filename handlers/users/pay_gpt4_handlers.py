import datetime
import re
from pprint import pprint

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, ChatTypeFilter
from aiogram.types import ChatType, Message, CallbackQuery
from asyncpg import Pool, UniqueViolationError

from keyboards.inline.vip_keyboard import to_payment_keyboard, buy_vip_callback, with_email_markup, no_email_markup, \
    get_click_after_buy_keyboard, gpt4_to_payment_keyboard, gpt4_no_email_markup, gpt4_with_email_markup, \
    gpt4_get_click_after_buy_keyboard
from loader import dp, time_delta
from states.generation_states import PaymentsState, GenerateText, GPT4PaymentsState
from utils.tinkoff_payments_api import tinkoff_payments


@dp.message_handler(Command("vip"), ChatTypeFilter([ChatType.PRIVATE]),state='*')
async def vip_1(message: Message, state : FSMContext):
    await state.reset_state()
    await message.answer(f'''
Про версия бота дает 50 ответов от нейросети длиной до 1500 знаков.

Контекст не запоминается, бот сделан для решения рабочих задач, а для беседы подойдет бот <a href="https://t.me/GPT_Kolersky_bot">GPT-3,5</a>😇

! Пока-что OpenAI не открыли функцию обработки изображений.

Стоимость: 590 руб

Чтобы купить нажмите на кнопку ниже''', reply_markup=gpt4_to_payment_keyboard, disable_web_page_preview=True)

@dp.callback_query_handler(buy_vip_callback.filter(level="1", to="gpt4_first"), ChatTypeFilter([ChatType.PRIVATE]), state=(GPT4PaymentsState.EnterEmail, None))
async def vip_1_call(call: CallbackQuery, state : FSMContext):
    await call.answer()
    await state.reset_state()
    await call.message.edit_text(f'''
Про версия бота дает 50 ответов от нейросети длиной до 1500 знаков.

Контекст не запоминается, бот сделан для решения рабочих задач, а для беседы подойдет бот <a href="https://t.me/GPT_Kolersky_bot">GPT-3,5</a>😇

! Пока-что OpenAI не открыли функцию обработки изображений.

Стоимость: 590 руб

Чтобы купить нажмите на кнопку ниже''', reply_markup=gpt4_to_payment_keyboard, disable_web_page_preview=True)

@dp.callback_query_handler(buy_vip_callback.filter(level="0", to = "gpt4_pay"))
async def enter_email(call : CallbackQuery, pool:Pool):
    await call.answer()
    async with pool.acquire() as con:
        email = await con.fetchval(f'''select email from users where user_id = {call.from_user.id}''')

    await GPT4PaymentsState.EnterEmail.set()

    if email:
        await call.message.edit_text(f"Введите свой емейл\n\nСохраненный емейл: {email}", reply_markup=gpt4_with_email_markup)
    else:
        await call.message.edit_text(f"Введите свой емейл", reply_markup=gpt4_no_email_markup)


@dp.callback_query_handler(buy_vip_callback.filter(level = "1", to = "gpt4_w_email"), state=GPT4PaymentsState.EnterEmail)
async def with_email(call : CallbackQuery, pool:Pool, state : FSMContext):
    await call.answer()
    await state.reset_state()

    async with pool.acquire() as con:
        email = await con.fetchval(f'''select email from users where user_id = {call.from_user.id}''')
        OrderId = "gpt4.1_" + str(await con.fetchval(f'insert into payments(user_id) values ({call.from_user.id}) returning OrderId'))

    resp =  await tinkoff_payments.init(Quantity=1, PriceOne=590_00, OrderId=OrderId, Description="Бот с нейросетью",
                                        DATA={"User_id" : call.from_user.id, "Email" : email}, Email=email)
    link = resp['PaymentURL']

    await call.message.edit_text(f'''
После оплаты нажмите на кнопку 'Проверить оплату ✅ '

❗️ВАЖНО: Оплачивайте по этой ссылке только один раз

Если вы оплатили, но пишет что оплата не найдена, просто попробуйте через 10-30 секунд ⏳

Ссылка на оплату: {link}''', reply_markup=gpt4_get_click_after_buy_keyboard(link, OrderId=OrderId))


@dp.message_handler(ChatTypeFilter([ChatType.PRIVATE]), state=GPT4PaymentsState.EnterEmail)
async def show_link_3(message : Message, pool:Pool, state : FSMContext):
    match = re.match("(?P<email>\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+)", message.text)

    if not match:
        await message.answer("Ошибка, введите емейл в правильном формате")
        return

    email = match.group("email")
    await state.reset_state()

    async with pool.acquire() as con:
        await con.execute(f'''update users set email = '{message.text}' where user_id = {message.from_user.id}''')
        OrderId = "gpt4.1_" + str(await con.fetchval(f'insert into payments(user_id) values ({message.from_user.id}) returning OrderId'))


    resp = await tinkoff_payments.init(Quantity=1, PriceOne=590_00, OrderId=OrderId, Description="Бот с нейросетью",
                                       DATA={"User_id": message.from_user.id, "Email" : email}, Email=email)
    link = resp['PaymentURL']

    await message.answer(f'''
После оплаты нажмите на кнопку 'Проверить оплату ✅ '

❗️ВАЖНО: Оплачивайте по этой ссылке только один раз

Если вы оплатили, но пишет что оплата не найдена, просто попробуйте через 10-30 секунд ⏳

Ссылка на оплату: {link}''', reply_markup=gpt4_get_click_after_buy_keyboard(link, OrderId=OrderId))


@dp.callback_query_handler(buy_vip_callback.filter(level="2", to = "gpt4_check"))
async def check_payment(call : CallbackQuery, callback_data : dict, pool : Pool):
    res = await tinkoff_payments.check_order(OrderId= callback_data['OrderId'])
    payments = res['Payments']

    if not payments:
        await call.answer("Оплата за данной ссылкой не найдена", show_alert=True)
        return

    payment_paid : dict = None
    for payment in payments:
        if payment['Status']=='CONFIRMED':
            payment_paid = payment
            break

    if payment_paid is None:
        await call.answer("Оплата за данной ссылкой не найдена", show_alert=True)
        return


    async with pool.acquire() as con:
        sql = f'''Update payments set Amount = {payment_paid["Amount"]}, PaymentId = '{payment_paid["PaymentId"]}', RRN = '{payment_paid.get("RRN")}',
Status = '{payment_paid.get("Status")}', datetime = '{(datetime.datetime.now() + time_delta).strftime("%Y-%m-%d %H:%M:%S")}'::timestamp 
where OrderId= {callback_data['OrderId'].split("_")[-1]}'''.replace("'None'", "null")
        await con.execute(sql)

        data = await con.fetchrow(f'''Update users set num_of_tries_text = num_of_tries_text + 50 where user_id = {call.from_user.id} 
        returning num_of_tries_text''')

    await GenerateText.S1.set()
    await call.message.answer(f'''
Оплата прошла успешно

Количество использований

Текст: {data['num_of_tries_text']}''')

    try:
        await call.message.delete()
    except Exception:
        pass
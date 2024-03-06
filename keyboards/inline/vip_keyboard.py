from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

buy_vip_callback = CallbackData("b_vip", "level", "to", "OrderId")

def get_buy_vip_callback(level = '', to= '', OrderId = ''):
    return buy_vip_callback.new(level=level,to=to, OrderId=OrderId)

to_payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Купить", callback_data=get_buy_vip_callback(level="0", to="pay"))]
])

no_email_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=get_buy_vip_callback(level="1", to="first"))]
])

with_email_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Использовать сохраненный емейл", callback_data=get_buy_vip_callback(level="1", to="w_email"))],
    [InlineKeyboardButton(text="Назад", callback_data=get_buy_vip_callback(level="1", to="first"))]
])


def get_click_after_buy_keyboard(url : str, OrderId):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Оплатить 💰", url=url)],
        [InlineKeyboardButton("Проверить оплату ✅", callback_data=get_buy_vip_callback(level="2", to="check", OrderId=OrderId))]
    ])
    return markup


gpt4_to_payment_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Купить", callback_data=get_buy_vip_callback(level="0", to="gpt4_pay"))]
])

gpt4_no_email_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=get_buy_vip_callback(level="1", to="gpt4_first"))]
])

gpt4_with_email_markup = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Использовать сохраненный емейл", callback_data=get_buy_vip_callback(level="1", to="gpt4_w_email"))],
    [InlineKeyboardButton(text="Назад", callback_data=get_buy_vip_callback(level="1", to="gpt4_first"))]
])


def gpt4_get_click_after_buy_keyboard(url : str, OrderId):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Оплатить 💰", url=url)],
        [InlineKeyboardButton("Проверить оплату ✅", callback_data=get_buy_vip_callback(level="2", to="gpt4_check", OrderId=OrderId))]
    ])
    return markup
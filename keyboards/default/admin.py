from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

admin_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Рассылка")

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Назад")

send_kb = ReplyKeyboardMarkup(resize_keyboard=True).add("Отправить").add("Назад")
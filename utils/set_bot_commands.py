from aiogram import types
from aiogram.types import BotCommandScopeAllPrivateChats, BotCommandScopeChat
from aiogram.utils.exceptions import ChatNotFound

from loader import admins


async def set_default_commands(dp):
    user_scope = [
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("my_profile", "Мой профиль"),
        types.BotCommand("vip", "Оплата"),
    ]
    await dp.bot.set_my_commands(user_scope, scope=BotCommandScopeAllPrivateChats())

    for admin in admins:
        try:
            await dp.bot.set_my_commands([types.BotCommand("admin", "Меню Админа")] + user_scope , scope=BotCommandScopeChat(admin))
        except ChatNotFound:
            pass


from aiogram import Dispatcher

from .throttling import ThrottlingMiddleware
from .database import DatabaseMiddleware


def setup(dp: Dispatcher):
    #dp.middleware.setup(ThrottlingMiddleware())
    pass

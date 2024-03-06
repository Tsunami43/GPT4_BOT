import asyncio
import datetime

import tiktoken
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.fsm_storage.redis import RedisStorage2

#from async_openai import OpenAI

from data import config
from data.config import OPENAI_TOKEN, OPENAI_ORGANIZATION_ID

bot = Bot(token=config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(pool_size=100,db=3)
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()

admins = []

# OpenAI.configure(
#     api_key = OPENAI_TOKEN,
#     debug_enabled = False,
# )

openai_headers = {"Authorization":"Bearer "+OPENAI_TOKEN, "OpenAI-Organization":OPENAI_ORGANIZATION_ID}

exceptions_chat_id = None
time_delta = datetime.timedelta(hours=0)

encoder = tiktoken.encoding_for_model("gpt-4")

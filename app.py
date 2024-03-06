# import asyncpg
#
# from middlewares.check_before_processing import CheckBeforeProcessing
# from utils.set_bot_commands import set_default_commands
#
#
# async def on_startup(dp):
#     import filters
#     filters.setup(dp)
#     #middlewares.setup(dp)
#     #import middlewares
#
#     from middlewares import DatabaseMiddleware
#
#     from data.config import DB_USER, DB_HOST, DB_NAME, DB_PASS
#     pool: asyncpg.Pool = await asyncpg.create_pool(user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME, max_size=100)
#
#     dp.middleware.setup(DatabaseMiddleware(pool))
#     dp.middleware.setup(CheckBeforeProcessing(pool))
#
#     from utils.notify_admins import on_startup_notify
#     await on_startup_notify(dp)
#     await set_default_commands(dp)
#
# if __name__ == '__main__':
#     from aiogram import executor
#     from handlers import dp
#
#     executor.start_polling(dp, on_startup=on_startup)



import asyncpg
from data.config import WEBHOOK_PATH, WEBAPP_PORT, WEBAPP_HOST, ssl_context
from aiogram.dispatcher.webhook import get_new_configured_app
from aiogram.utils.executor import start_webhook

from middlewares.check_before_processing import CheckBeforeProcessing
from utils.set_bot_commands import set_default_commands
from loader import loop

async def on_startup(dp):
    import filters
    filters.setup(dp)
    #middlewares.setup(dp)
    #import middlewares

    from middlewares import DatabaseMiddleware

    from data.config import DB_USER, DB_HOST, DB_NAME, DB_PASS
    pool: asyncpg.Pool = await asyncpg.create_pool(user=DB_USER, password=DB_PASS, host=DB_HOST, database=DB_NAME, max_size=100)
    dp.middleware.setup(DatabaseMiddleware(pool))
    dp.middleware.setup(CheckBeforeProcessing(pool))

    from data.config import WEBHOOK_URL, SSL_CERTIFICATE
    await dp.bot.set_webhook(url=WEBHOOK_URL, certificate=SSL_CERTIFICATE)

    from utils.notify_admins import on_startup_notify
    await on_startup_notify(dp)
    await set_default_commands(dp)

if __name__ == '__main__':
    from handlers import dp


    app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)

    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        host = WEBAPP_HOST,
        port = WEBAPP_PORT,
        ssl_context = ssl_context,
        #skip_updates=True,
        loop = loop
    )

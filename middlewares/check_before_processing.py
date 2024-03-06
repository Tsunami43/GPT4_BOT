
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, ChatType, CallbackQuery


class CheckBeforeProcessing(BaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def on_pre_process_message(self, message : Message, data : dict):
        async with self.pool.acquire() as con:
            if message.from_user.username:
                await con.execute(f'''update users set username = '{message.from_user.username}' where user_id = {message.from_user.id}''')


            is_exist = await con.fetchval(f'''select exists(select 1 from users where user_id = {message.from_user.id})''')
            if (message.text and not message.text.startswith("/start")) and not is_exist:
                await con.execute(f'''insert into users(user_id, username, first_name, full_name, deeplink, datetime) values
                ({message.from_user.id}, '{message.from_user.username}', '{message.from_user.first_name.replace("'", "''")}',
                '{message.from_user.full_name.replace("'", "''")}',  'middleware', '{message.date.strftime("%Y-%m-%d %H:%M:%S")}'::timestamp) ON conflict(user_id) do nothing'''.replace("'None'", "null"))

            is_subscribed = await con.fetchval(f'''select (select num_of_tries_text from users where user_id = {message.from_user.id})>0''')
            data['is_subscribed'] = is_subscribed if is_subscribed else False


from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware



class DatabaseMiddleware(LifetimeControllerMiddleware):
    skip_patterns = ['update']
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def pre_process(self, obj, data, *args):
        data['pool'] = self.pool

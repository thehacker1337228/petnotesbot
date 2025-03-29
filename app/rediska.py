from aiogram.fsm.storage.redis import RedisStorage
from typing import Any, Awaitable, Callable, Dict #типы импортируем для мидлваре
from aiogram.enums.parse_mode import ParseMode
from aiogram import BaseMiddleware
from aiogram.types import Message

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage):
        self.storage = storage
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: Dict[str, Any]) -> Any:
        user = f'user{event.from_user.id}'
        check_user = await self.storage.redis.get(name=user)
        if check_user:
            if int(check_user.decode()) == 1:
                await self.storage.redis.set(name=user, value = 0, ex = 5) #на сколько секунд бан
                return await event.answer("❌ Слишком много запросов подряд. Пожалуйста, подождите 5 секунд")
            return
        await self.storage.redis.set(name=user, value = 1, px = 500) #раз в сколько секунд можно делать запрос
        return await handler(event, data)


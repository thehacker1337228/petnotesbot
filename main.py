from config import TOKEN


import asyncio
from aiogram import Bot, Dispatcher, F, BaseMiddleware
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton #юзаем реплай клаву
from aiogram.filters import CommandStart,Command
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from services.note_requests import NoteRequests
from services.user_requests import UserRequests
from services.pages_service import PagesService
from services.user_service import UserDto
from app.rediska import ThrottlingMiddleware

from services.models import init_main

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties

from aiogram.methods.delete_message import DeleteMessage



from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage #импорт редис




class TelegramBot:
    from app.bot_handlers import setup_handlers
    def __init__(self, token, need_init = False):
        self.bot = Bot(token=token, session=AiohttpSession(), default=DefaultBotProperties(parse_mode='HTML'))

        self.storage = RedisStorage.from_url("redis://localhost:6379/0") #redis server хранилизн
        self.dp = Dispatcher(storage=self.storage)

        self.dp.message.middleware.register(ThrottlingMiddleware(storage=self.storage))


        self.pages_service = PagesService()
        self.user_requests = UserRequests()
        self.note_requests = NoteRequests()

    async def start_command(self, message: Message): #видимо мы переметим это из хендлеров
        """Обработчик команды /start"""
        await message.answer("Привет, я твой бот!")


    async def login(self, message: Message):
        """Логин пользователя"""
        user = message.from_user

        self.id = user.id
        self.username = user.username


        self.check_status = await self.user_requests.check(message.from_user.id)
        if self.check_status == 0:
            new_user = UserDto(message.from_user.id, message.from_user.username, state="start", json_data="start")
            await self.user_requests.add(new_user)
            await message.answer("Вы успешно зарегистрировались")
            print("юзер добавлен")
        else:
            print("юзер уже существует")
            await message.answer("Успешная авторизация!")


    async def run(self):
        """Запуск бота"""
        print("База данных и таблицы созданы!")
        await init_main()  # Инитим ОRM NEW
        await self.setup_handlers()
        await self.dp.start_polling(self.bot)


if __name__ == "__main__":
    token = TOKEN
    bot = TelegramBot(token)

    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("Выходим")
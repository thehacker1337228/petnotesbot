from config import TOKEN

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton #юзаем реплай клаву
from aiogram.filters import CommandStart,Command
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from services.note_requests import NoteRequests
from services.user_requests import UserRequests
from services.pages_service import PagesService
from services.user_service import UserService, UserDto
from services.note_service import NoteService

from services.models import init_main

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.bot import DefaultBotProperties

from aiogram.methods.delete_message import DeleteMessage


class TelegramBot:
    from app.bot_handlers import setup_handlers
    def __init__(self, token, need_init = False):
        self.bot = Bot(token=token, session=AiohttpSession(), default=DefaultBotProperties(parse_mode='HTML'))
        self.dp = Dispatcher()

        self.note_service = NoteService()
        self.user_service = UserService() #Инитим Юзер Сервис
        self.pages_service = PagesService()
        self.user_requests = UserRequests()
        self.note_requests = NoteRequests()

        #if (need_init): ИНИТИМ ТАБЛИЧКИ
        self.note_service.init()
        self.user_service.init()


        #self.setup_handlers()  # Регистрация обработчиков
        #self.dp.include_self.dp(self.dp) #роутеры хендлеров



    async def login(self, message: Message):
        """Логин пользователя"""
        user = message.from_user

        self.id = user.id
        self.username = user.username
        #self.check = self.user_service.check(self.id)
        #self.check = self.user_requests.check(self.id) #CHECK NEW

        self.check_status = await self.user_requests.check(message.from_user.id)
        if self.check_status == 0:
            new_user = UserDto(message.from_user.id, message.from_user.username, state="start", json_data="start")
            await self.user_requests.add(new_user)
            await message.answer("Вы успешно зарегистрировались")
            print("юзер добавлен")
        else:
            print("юзер уже существует")
            await message.answer("Успешная авторизация!")


        #if self.check == 0: #СТАРЫЙ ЧЕК
        #    new_user = UserDto(message.from_user.id, message.from_user.username, state="start")
        #    self.user_service.add(new_user)  # Метод add внутри UserService принимает объект UserDto
        #    await message.answer("Вы успешно зарегистрировались")
        #await message.answer("Успешная авторизация!")



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
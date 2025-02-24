from config import TOKEN

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton #юзаем реплай клаву
from aiogram.filters import CommandStart,Command
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

from services.user_service import UserService, UserDto
from services.note_service import NoteService, NoteDto


class TelegramBot:
    from app.bot_handlers import setup_handlers
    def __init__(self, token, need_init = False):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.logged_users = {}
        self.note_service = NoteService()
        self.user_service = UserService() #Инитим Юзер Сервис

        #if (need_init): ИНИТИМ ТАБЛИЧКИ
        self.note_service.init()
        self.user_service.init()

        #self.setup_handlers()  # Регистрация обработчиков
        #self.dp.include_self.dp(self.dp) #роутеры хендлеров



    async def login(self, message: Message):
        """Логин пользователя"""
        user = message.from_user
        user_data = {
            "telegram_id": user.id,
            "full_name": user.full_name,
            "username": user.username,
            "language_code": user.language_code,
            "is_bot": user.is_bot
        }
        self.logged_users[user.id] = user_data
        self.id = user.id
        self.username = user.username

        self.check = self.user_service.check(self.id)
        if self.check == 0:
            new_user = UserDto(message.from_user.id, message.from_user.username, state="start")
            self.user_service.add(new_user)  # Метод add внутри UserService принимает объект UserDto
            await message.answer("Вы успешно зарегистрировались")
        await message.answer("Успешная авторизация!")

    async def show_all(self,user_id):
        notes = self.note_service.get_all(user_id)
        if not notes:
            #await message.answer("У вас нет заметок.")
            result = "У вас нет заметок"
            return result
        else:
            result = "=====[ Заметки ]=====\n"
            for note in notes:
                result += f"Заголовок: {note.title}\nКонтент:{note.content}\nID заметки: {note.note_id}\n\n"
            return result


    async def run(self):
        """Запуск бота"""
        await self.setup_handlers()
        await self.dp.start_polling(self.bot)





if __name__ == "__main__":
    token = TOKEN
    bot = TelegramBot(token)
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("Выходим")
from config import TOKEN

import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton #юзаем реплай клаву
from aiogram.filters import CommandStart,Command
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


from services.user_service import UserService, UserDto
from services.note_service import NoteService, NoteDto
from enum import Enum
import json
import random
import time
import app.keyboards as kb


class SessionState(Enum):
    LOGIN = "login"
    MENU = "menu"
    ADD_NOTE = "add_note"
    NOTES_LIST = "notes_list"
    DEL_NOTE = "del_note"
    EDIT_NOTE = "edit_note"

class AddNote(StatesGroup):  # конструктор добавления заметок
    name = State()
    content = State()

class DelNote(StatesGroup):  # конструктор удаления заметок
    note_id = State()

class EditNote(StatesGroup):  # конструктор изменения заметок
    note_id = State()
    content = State()

class TelegramBot:

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




    def setup_handlers(self):
        @self.dp.message(CommandStart())
        async def start_command(message: Message):
            await self.login(message)
            await message.answer(
                f"Привет, {message.from_user.first_name}. Твой TG ID: {message.from_user.id}. Готов помочь с твоими заметками! ",
                reply_markup=kb.main)

        @self.dp.message(F.text == "Добавить")
        async def add_one(message: Message, state: FSMContext):
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            user.state = SessionState.ADD_NOTE.value
            self.user_service.update(user)  # апдейтим стейт
            await state.set_state(AddNote.name)  # шаг 1 input имени заметки
            await message.answer("Введите заголовок заметки:")

        @self.dp.message(AddNote.name)  # ловим что юзер вводит имя
        async def add_two(message: Message, state: FSMContext):
            await state.update_data(name=message.text)  # сохраняем в кэше
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            user.json_data = json.dumps({"add_title": (await state.get_data()).get("name")}, ensure_ascii=False)
            self.user_service.update(user)  # апдейтим json
            await state.set_state(AddNote.content)  # след. шан input контента
            await message.answer("Введите вашу заметку:")

        @self.dp.message(AddNote.content)  # ловим что юзер вводит content
        async def two_three(message: Message, state: FSMContext):
            await state.update_data(content=message.text)  # сохраняем в кэше
            data = await state.get_data()  # достаём информацию и можно отправить в базу данных
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            user.json_data = json.dumps({"add_content": data["content"]}, ensure_ascii=False)
            self.user_service.update(user)  # апдейтим json
            note = NoteDto(message.from_user.id, data["name"],data["content"])
            self.note_service.add(note)

            await message.answer("Заметка добавлена!")
            await message.answer(f"Заголовок: {data['name']} \nКонтент: {data['content']}", reply_markup=kb.main)

            user.json_data = json.dumps({"add_done": data["content"]}, ensure_ascii=False)
            user.state = SessionState.MENU.value
            self.user_service.update(user)  # апдейтим json

            await state.clear()

        @self.dp.message(F.text == "Мои заметки")
        async def show(message: Message):
            await message.answer(await self.show_all(message.from_user.id),
                                 reply_markup=kb.main)  # мы это делаем потому, что если использовать self.id получается баг
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            user.state = SessionState.NOTES_LIST.value
            self.user_service.update(user)  # апдейтим state


        @self.dp.message(F.text == "Удалить заметку")
        async def del_nts(message: Message, state: FSMContext):
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            user.state = SessionState.DEL_NOTE.value
            self.user_service.update(user)  # апдейтим state
            await message.answer(await self.show_all(message.from_user.id))
            await state.set_state(DelNote.note_id)
            await message.answer("Введите ID заметки, которую хотите удалить")


        @self.dp.message(DelNote.note_id)  # ловим что юзер вводит note_id
        async def del_two(message: Message, state: FSMContext):
            await state.update_data(note_id=message.text)  # сохраняем в кэше note_id
            data = await state.get_data()
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            self.note_service.delete(data["note_id"])
            await message.answer("Заметка удалена!", reply_markup=kb.main)
            user.json_data = json.dumps({"del_done": data["note_id"]}, ensure_ascii=False)
            user.state = SessionState.MENU.value
            self.user_service.update(user)  # апдейтим json
            await state.clear()

        @self.dp.message(F.text == "Редактировать заметку")
        async def edit_nts(message: Message, state: FSMContext):
            await message.answer(await self.show_all(message.from_user.id))
            await state.set_state(EditNote.note_id)
            await message.answer("Введите ID заметки, которую хотите изменить:")
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            user.state = SessionState.EDIT_NOTE.value
            self.user_service.update(user)  # апдейтим state

        @self.dp.message(EditNote.note_id)  # ловим что юзер вводит note_id
        async def edit_two(message: Message, state: FSMContext):
            await state.update_data(note_id=message.text)  # сохраняем в кэше note_id
            data = await state.get_data()
            note = self.note_service.get_note(data["note_id"])  # получаем ноту по note_id, чтобы вывести контент
            await message.answer(note.content)
            await state.set_state(EditNote.content)  # след. шан input контента
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            json_data = json.dumps({"edit_index": data["note_id"]}, ensure_ascii=False)
            user.json_data = json_data
            self.user_service.update(user)  # апдейтим json
            await message.answer("Введите новый текст заметки:")

        @self.dp.message(EditNote.content)  # ловим что юзер вводит новый контент
        async def edittwo_three(message: Message, state: FSMContext):
            await state.update_data(content=message.text)  # сохраняем в кэше
            data = await state.get_data()  # достаём информацию и можно отправить в базу данных
            user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
            user.json_data = json.dumps({"edit_done": data["content"]}, ensure_ascii=False)
            note = self.note_service.get_note(data["note_id"])  # получаем ноту по note_id
            note.content = data["content"]
            note.updated_at = round(time.time())
            self.note_service.update(note)
            user.state = SessionState.EDIT_NOTE.value
            self.user_service.update(user)  # апдейтим json и state
            await message.answer("Заметка изменена", reply_markup=kb.main)
            await state.clear()

    
    async def run(self):
        """Запуск бота"""
        self.setup_handlers()
        await self.dp.start_polling(self.bot)





if __name__ == "__main__":
    token = TOKEN
    bot = TelegramBot(token)
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("Выходим")
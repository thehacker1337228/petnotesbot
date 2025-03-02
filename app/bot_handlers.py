from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import app.keyboards as kb
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from services.note_service import NoteDto
from services.pages_service import PagesService
from aiogram.types import CallbackQuery

from aiogram.methods.delete_message import DeleteMessage


from enum import Enum
import json
import time

class AddNote(StatesGroup):  # конструктор добавления заметок
    name = State()
    content = State()

class DelNote(StatesGroup):  # конструктор удаления заметок
    note_id = State()

class EditNote(StatesGroup):  # конструктор изменения заметок
    note_id = State()
    content = State()

class SessionState(Enum):
    LOGIN = "login"
    MENU = "menu"
    ADD_NOTE = "add_note"
    NOTES_LIST = "notes_list"
    DEL_NOTE = "del_note"
    EDIT_NOTE = "edit_note"



async def setup_handlers(self):
    @self.dp.message(CommandStart())
    async def start_command(message: Message, state: FSMContext):
        await state.clear()
        await self.login(message)
        await message.answer(
            f"Привет, {message.from_user.first_name}. Твой TG ID: {message.from_user.id}. Готов помочь с твоими заметками! ",
            reply_markup=kb.main)


    @self.dp.message(F.text == "Отменить")
    async def cancel_handler(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Операция отменена", reply_markup=kb.main)


    @self.dp.message(F.text.contains("📑")) #список заметок
    async def inline_list(message:Message):
        pages = PagesService()
        titles = await pages.list(message.from_user.id)
        keyboard = await pages.gen_inline(titles)
        await message.answer("Список заметок", reply_markup=keyboard)

    @self.dp.callback_query(lambda callback: callback.data.startswith("nxt_"))
    async def nxt_page(callback: CallbackQuery):
        current_page = int(callback.data.split("_")[1])
        pages = PagesService()
        scope = await pages.list_scope(callback.from_user.id)
        keyboard = await pages.gen_inline_scope(scope, current_page=current_page + 1)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()







    @self.dp.callback_query(lambda callback: callback.data.startswith("next_"))
    async def next_page(callback: CallbackQuery):
        current_page = int(callback.data.split("_")[1])
        pages = PagesService()
        titles = await pages.list(callback.from_user.id)
        keyboard = await pages.gen_inline(titles,current_page=current_page+1)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

    @self.dp.callback_query(lambda callback: callback.data.startswith("prev_"))
    async def prev_page(callback: CallbackQuery):
        current_page = int(callback.data.split("_")[1])
        pages = PagesService()
        titles = await pages.list(callback.from_user.id)
        keyboard = await pages.gen_inline(titles, current_page=current_page - 1)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()

    @self.dp.callback_query(lambda callback: callback.data == "предел")
    async def page_limit(callback: CallbackQuery):
        await callback.answer("Достигнут предел страниц")

    @self.dp.callback_query(lambda callback: callback.data.startswith("note_"))
    async def note_num(callback: CallbackQuery):
        note_index = int(callback.data.split("_")[1])
        note = self.note_service.get_note(note_index)  # получаем ноту по note_id
        result = f"<b>📌 {note.title}</b>\n📄 {note.content}"
        pages = PagesService()
        titles = await pages.list(callback.from_user.id)
        keyboard = await pages.gen_inline(titles, force=True)
        await callback.message.answer(result, reply_markup=keyboard)
        #await callback.answer(f"Заметка с note_id {note_index}") #высплывающее техническое сообщение
        await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


    @self.dp.message(F.text.contains("📌")) #Добавить заметку
    async def add_one(message: Message, state: FSMContext):
        user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
        user.state = SessionState.ADD_NOTE.value
        self.user_service.update(user)  # апдейтим стейт
        await state.set_state(AddNote.name)  # шаг 1 input имени заметки
        await message.answer("Введите заголовок заметки:",reply_markup=kb.cancel_button)

    @self.dp.message(AddNote.name)  # ловим что юзер вводит имя
    async def add_two(message: Message, state: FSMContext):
        await state.update_data(name=message.text)  # сохраняем в кэше
        user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
        user.json_data = json.dumps({"add_title": (await state.get_data()).get("name")}, ensure_ascii=False)
        self.user_service.update(user)  # апдейтим json
        await state.set_state(AddNote.content)  # след. шан input контента
        await message.answer("Введите вашу заметку:",reply_markup=kb.cancel_button)

    @self.dp.message(AddNote.content)  # ловим что юзер вводит content
    async def two_three(message: Message, state: FSMContext):
        await state.update_data(content=message.text)  # сохраняем в кэше
        data = await state.get_data()  # достаём информацию и можно отправить в базу данных
        user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
        user.json_data = json.dumps({"add_content": data["content"]}, ensure_ascii=False)
        self.user_service.update(user)  # апдейтим json
        note = NoteDto(message.from_user.id, data["name"], data["content"])
        self.note_service.add(note)

        await message.answer("Заметка добавлена!")
        await message.answer(f"Заголовок: {data['name']} \nКонтент: {data['content']}", reply_markup=kb.main)

        user.json_data = json.dumps({"add_done": data["content"]}, ensure_ascii=False)
        user.state = SessionState.MENU.value
        self.user_service.update(user)  # апдейтим json

        await state.clear()

    @self.dp.message(F.text.contains("🗒️")) #Мои заметки (заметки скопом)
    async def show(message: Message):
        #await message.answer(await self.show_all(message.from_user.id),
        #                     reply_markup=kb.main)  # мы это делаем потому, что если использовать self.id получается баг
        pages = PagesService()
        scope = await pages.list_scope(message.from_user.id)
        keyboard = await pages.gen_inline_scope(scope)

        await message.answer(await self.show_all(message.from_user.id),
                             reply_markup=keyboard)  # мы это делаем потому, что если использовать self.id получается баг

        user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
        user.state = SessionState.NOTES_LIST.value
        self.user_service.update(user)  # апдейтим state

    @self.dp.message(F.text.contains("❌")) #Удалить заметки
    async def del_nts(message: Message, state: FSMContext):
        user = self.user_service.get(message.from_user.id)  # раскатываем дто объект юзера обязательно заново
        user.state = SessionState.DEL_NOTE.value
        self.user_service.update(user)  # апдейтим state
        await message.answer(await self.show_all(message.from_user.id))
        await state.set_state(DelNote.note_id)
        await message.answer("Введите ID заметки, которую хотите удалить",reply_markup=kb.cancel_button)

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

    @self.dp.message(F.text.contains("✏️"))
    async def edit_nts(message: Message, state: FSMContext):
        await message.answer(await self.show_all(message.from_user.id))
        await state.set_state(EditNote.note_id)
        await message.answer("Введите ID заметки, которую хотите изменить:",reply_markup=kb.cancel_button)
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
        await message.answer("Введите новый текст заметки:",reply_markup=kb.cancel_button)

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


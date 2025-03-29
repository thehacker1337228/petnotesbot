from config import ADMIN_ID


from aiogram import F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from app.keyboards import kb
from app.keyboards import ikb

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


from services.note_service import NoteDto
from aiogram.types import CallbackQuery
from aiogram.methods.delete_message import DeleteMessage


from enum import Enum
import json
import time

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError
from services.user_requests import UserRequests  # Твой сервис для работы с БД


class AddNote(StatesGroup):  # конструктор добавления заметок
    name = State()
    content = State()


class DeleteNote(StatesGroup): # новый конструктор удаления заметок
    note_id = State()

class EditNote(StatesGroup):  # конструктор изменения заметок
    note_id = State()
    content = State()

class BroadcastText(StatesGroup):
    users_list = State()
    content = State()

class SessionState(Enum):
    LOGIN = "login"
    MENU = "menu"
    ADD_NOTE = "add_note"
    NOTES_SCOPE = "notes_scope"
    NOTES_LIST = "notes_list"
    DEL_NOTE = "del_note"
    EDIT_NOTE = "edit_note"


async def setup_handlers(self):
    MAX_NOTES = 750
    MAX_LENGTH = 4000
    @self.dp.message(CommandStart())
    async def start_command(message: Message, state: FSMContext):
        await state.clear()
        await self.login(message)
        if message.chat.type != "private":
            await message.answer("❌ Бот работает только в личных сообщениях!")
            return

        await message.answer(
            f"Привет, {message.from_user.first_name}. Твой TG ID: {message.from_user.id}. Готов помочь с твоими заметками! ",
            reply_markup=kb.main)

    #о разработчике
    @self.dp.message(Command("about"))
    async def about_handler(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Главный создатель приложения: Arturio Agre. Хотите такого бота? Хотите бота на заказ любой сложности? 💼Связывайтесь с генеральным директором: @arturio_agre",
                             reply_markup=kb.main)




    #Отменятор любого fsmState
    @self.dp.message(F.text == "Отменить")
    async def cancel_handler(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Операция отменена", reply_markup=kb.main)

    # рассылка всем юзерам бота
    @self.dp.message(F.text.contains("рассылка"))
    async def broadcast_command(message: Message, state: FSMContext):
        if message.from_user.id == ADMIN_ID:
            users = await self.user_requests.get_all_users()
            users_list = [user.tg_id for user in users]  # Сразу создаем список ID пользователей
            await message.answer(f"Кол-во пользователей для рассылки: {len(users_list)}")
            await message.answer("Введите контент для броадкаста:", reply_markup=kb.cancel_button)
            await state.update_data(users_list=users_list)
            await state.set_state(BroadcastText.content)
        else:
            await message.answer("Вы не админ")
            await state.clear()

    # Хендлер для получения контента и отправки сообщений пользователям
    @self.dp.message(BroadcastText.content)
    async def edit_note_two(message: Message, state: FSMContext):
        await state.update_data(content=message.text)
        data = await state.get_data()
        cnt = 0
        for tg_id in data["users_list"]:
            try:
                await self.bot.send_message(tg_id, data["content"])
                cnt += 1
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {tg_id}: {e}")
        await message.answer(f"Сообщение отправлено {cnt} пользователям.")
        await state.clear()

    # Обработчик клика по списку номерам страниц
    @self.dp.callback_query(F.data.contains("страница"))
    async def page_number(callback: CallbackQuery):
        await callback.answer()

    # список заметок кнопочками
    @self.dp.message(F.text.contains("📑"))
    async def inline_list(message:Message):

        titles = await self.pages_service.list(message.from_user.id)
        keyboard = await ikb.gen_inline(titles)
        await message.answer("Ваши заметки:" if titles else "У вас нет заметок", reply_markup=keyboard)
        user = await self.user_requests.get(message.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.state = SessionState.NOTES_LIST.value
        await self.user_requests.update(user)  # апдейтим state

    # Хендлеры для функции "Заметки СКОПОМ"
    @self.dp.callback_query(lambda callback: callback.data.startswith("nxt_"))
    async def nxt_page(callback: CallbackQuery):
        current_page = int(callback.data.split("_")[1])  # Получаем текущую страницу
        scope = await self.pages_service.list_scope(callback.from_user.id)  # Получаем все заметки
        content = await self.pages_service.scope_slice(scope, current_page + 1)  # Берём нужные
        keyboard = await ikb.gen_inline_scope(scope, current_page=current_page + 1)  # Обновляем клавиатуру
        await callback.message.edit_text(content, reply_markup=keyboard)
        await callback.answer()


    @self.dp.callback_query(lambda callback: callback.data.startswith("prv_"))
    async def prv_page(callback: CallbackQuery):
        current_page = int(callback.data.split("_")[1])  # Получаем текущую страницу
        scope = await self.pages_service.list_scope(callback.from_user.id)  # Получаем все заметки
        content = await self.pages_service.scope_slice(scope, current_page - 1)  # Берём нужные
        keyboard = await ikb.gen_inline_scope(scope, current_page=current_page - 1)  # Обновляем клавиатуру
        await callback.message.edit_text(content, reply_markup=keyboard)
        await callback.answer()


    # Удалятор ФСМ шаг 1 заметки из просмотрщика NEW
    @self.dp.callback_query(lambda callback: callback.data.startswith("del_"))
    async def del_note(callback: CallbackQuery, state: FSMContext):
        note_id = int(callback.data.split("_")[1])

        user = await self.user_requests.get(callback.from_user.id)  # New раскатываем дто объект юзера обязательно заново

        user.state = SessionState.DEL_NOTE.value # меняем state
        user.json_data = json.dumps({"del_note": note_id}, ensure_ascii=False)

        await self.user_requests.update(user)  # апдейтим user'a

        await state.set_state(DeleteNote.note_id)
        await state.update_data(note_id=note_id)


        await callback.message.answer("Вы действительно хотите удалить эту заметку?!", reply_markup=kb.delete_button)
        await callback.answer()

    # ФСМ шаг 2 в удалении заметок
    @self.dp.message(DeleteNote.note_id, F.text.contains("🗑️"))
    async def del_note_two(message: Message, state: FSMContext):
        data = await state.get_data()
        await self.note_requests.delete(data["note_id"], message.from_user.id) #непосредственно удаление
        await message.answer("Заметка удалена!", reply_markup=kb.main)

        user = await self.user_requests.get(message.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.json_data = json.dumps({"del_done": data["note_id"]}, ensure_ascii=False)
        user.state = SessionState.MENU.value
        await self.user_requests.update(user)  # апдейтим user'a

        await state.clear()


    @self.dp.message(DeleteNote.note_id)
    async def del_note_wrong_cmd(message: Message):
        await message.answer('🗑️ Неверная команда. Нажмите "Удалить заметку"!', reply_markup=kb.delete_button)

    # Изменятор из просмотрщика ФСМ шаг 1 NEW
    @self.dp.callback_query(lambda callback: callback.data.startswith("edit_"))
    async def edit_note_one(callback: CallbackQuery, state: FSMContext):
        note_id = int(callback.data.split("_")[1])
        await state.set_state(EditNote.note_id)
        await state.update_data(note_id=note_id)
        data = await state.get_data()

        user = await self.user_requests.get(callback.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.state = SessionState.EDIT_NOTE.value


        json_data = json.dumps({"edit_index": data["note_id"]}, ensure_ascii=False)
        user.json_data = json_data
        await self.user_requests.update(user)  # апдейтим user'a

        await state.set_state(EditNote.content)  # след. шан input контента
        await callback.message.answer("Введите новый текст заметки:", reply_markup=kb.cancel_button)
        await callback.answer()

    @self.dp.message(EditNote.content)
    async def edit_note_two(message: Message, state: FSMContext):
        await state.update_data(content=message.text)  # сохраняем в кэше
        data = await state.get_data()
        user = await self.user_requests.get(message.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.json_data = json.dumps({"edit_done": data["content"]}, ensure_ascii=False)
        note = await self.note_requests.get_note(data["note_id"])  # получаем ноту по note_id
        note.content = data["content"]
        note.updated_at = round(time.time())
        await self.note_requests.update(note)
        user.state = SessionState.MENU.value
        await self.user_requests.update(user)  # апдейтим user'a
        await message.answer("Заметка изменена", reply_markup=kb.main)
        await state.clear()



    # Хендлеры для функции СПИСОК ЗАМЕТОК
    @self.dp.callback_query(lambda callback: callback.data.startswith("next_"))
    async def next_page(callback: CallbackQuery):
        current_page = int(callback.data.split("_")[1])
        cnt = int(callback.data.split("_")[2])
        titles = await self.pages_service.list(callback.from_user.id)
        keyboard = await ikb.gen_inline(titles,current_page=current_page+1,force = True if cnt==1 else False)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()


    @self.dp.callback_query(lambda callback: callback.data.startswith("prev_"))
    async def prev_page(callback: CallbackQuery):
        current_page = int(callback.data.split("_")[1])
        cnt = int(callback.data.split("_")[2])
        titles = await self.pages_service.list(callback.from_user.id)
        keyboard = await ikb.gen_inline(titles, current_page=current_page - 1,force = True if cnt==1 else False)
        await callback.message.edit_reply_markup(reply_markup=keyboard)
        await callback.answer()


    @self.dp.callback_query(lambda callback: callback.data == "limit")
    async def page_limit(callback: CallbackQuery):
        await callback.answer("Достигнут предел страниц")

    # Просмотр заметки
    @self.dp.callback_query(lambda callback: callback.data.startswith("note_"))
    async def note_num(callback: CallbackQuery):
        note_index = int(callback.data.split("_")[1])
        current_page = int(callback.data.split("_")[2])
        note = await self.note_requests.get_note(note_index)  # получаем ноту по note_id
        result = f"<b>📌 {note.title}</b>\n📄 {note.content}"[:MAX_LENGTH]
        titles = await self.pages_service.list(callback.from_user.id)
        keyboard = await ikb.gen_inline(titles,current_page=current_page,force=True, note_id=note_index)
        await callback.message.edit_text(result, reply_markup=keyboard)
        #await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)

    # Добавить заметку ФСМ
    @self.dp.message(F.text.contains("📌"))
    async def add_one(message: Message, state: FSMContext):
        cnt = await self.note_requests.cnt(message.from_user.id)
        if cnt >= MAX_NOTES:
            await message.answer("Иссяк лимит памяти. Напишите администратору @arturio_agre")
            return
        user = await self.user_requests.get(message.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.state = SessionState.ADD_NOTE.value
        await self.user_requests.update(user)  # апдейтим user'a
        await state.set_state(AddNote.name)  # шаг 1 input имени заметки
        await message.answer("Введите заголовок заметки:",reply_markup=kb.cancel_button)


    @self.dp.message(AddNote.name)  # ловим что юзер вводит имя
    async def add_two(message: Message, state: FSMContext):
        await state.update_data(name=message.text[:MAX_LENGTH])  # сохраняем в кэше
        user = await self.user_requests.get(message.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.json_data = json.dumps({"add_title": (await state.get_data()).get("name")}, ensure_ascii=False)
        await self.user_requests.update(user)  # апдейтим user'a
        await state.set_state(AddNote.content)  # след. шан input контента
        await message.answer("Введите вашу заметку:",reply_markup=kb.cancel_button)


    @self.dp.message(AddNote.content)  # ловим что юзер вводит content
    async def two_three(message: Message, state: FSMContext):
        await state.update_data(content=message.text[:MAX_LENGTH])  # сохраняем в кэше
        data = await state.get_data()  # достаём информацию и можно отправить в базу данных
        user = await self.user_requests.get(message.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.json_data = json.dumps({"add_content": data["content"]}, ensure_ascii=False)
        await self.user_requests.update(user)  # апдейтим user'a

        note = NoteDto(message.from_user.id, data["name"], data["content"])


        await self.note_requests.add(note)

        await message.answer("Заметка добавлена!")
        await message.answer(f"Заголовок: {data['name']} \nКонтент: {data['content']}", reply_markup=kb.main)

        user.json_data = json.dumps({"add_done": data["content"]}, ensure_ascii=False)
        user.state = SessionState.MENU.value
        await self.user_requests.update(user)  # апдейтим user'a
        await state.clear()


    @self.dp.message(F.text.contains("🗒️")) #Мои заметки (заметки скопом)
    async def show(message: Message):
        scope = await self.pages_service.list_scope(message.from_user.id)
        keyboard = await ikb.gen_inline_scope(scope)
        await message.answer(await self.pages_service.scope_slice(scope), reply_markup=keyboard)

        user = await self.user_requests.get(message.from_user.id)  # New раскатываем дто объект юзера обязательно заново
        user.state = SessionState.NOTES_SCOPE.value
        await self.user_requests.update(user)  # апдейтим user'a


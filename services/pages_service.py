from services.note_service import NoteService
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import math
import asyncio



class PagesService:
    def __init__(self):
        self.note_service = NoteService()


    async def list(self,user_id):
        notes = self.note_service.get_all(user_id)
        titles = []
        for i in notes:
            titles.append((i.title,i.note_id))
        return titles

    async def list_scope(self,user_id):
        notes = self.note_service.get_all(user_id)
        if not notes:
            scope = "У вас нет заметок"
            return scope
        else:
            scope = "=====[ Заметки ]=====\n"
            for note in notes:
                scope += f"<b>{note.title}</b>\n{note.content}\n<i>ID: {note.note_id}</i>\n\n"

            return scope



    async def gen_inline(self,titles,current_page = 1, force=False):
        page_max = 5 #максимальное количество заметок на странице
        if force:
            page_max = 3
        page_number = math.ceil(len(titles)/page_max) #сколько всего страниц
        #keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=f"📋 {title}", callback_data=f"note_{note_id}")] for title, note_id in titles[page_max*current_page-page_max:page_max*current_page]]
        )


        # Новый ряд кнопок
        new_row = [
            InlineKeyboardButton(text="<-", callback_data=f"prev_{current_page}" if current_page>1 else "предел"),
            InlineKeyboardButton(text=f"{current_page}/{page_number} страница", callback_data="added2"),
            InlineKeyboardButton(text="->", callback_data=f"next_{current_page}" if current_page<page_number else "предел")
        ]

        # Добавляем новый ряд кнопок
        keyboard.inline_keyboard.append(new_row)
        return keyboard

    async def gen_inline_scope(self,scope, current_page=1):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        symbol_max = 4096  # максимальное количество заметок на странице
        page_number = math.ceil(len(scope) / symbol_max)  # сколько всего страниц
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])

        new_row = [
            InlineKeyboardButton(text="<-", callback_data=f"prev_{current_page}" if current_page>1 else "предел"),
            InlineKeyboardButton(text=f"{current_page}/{page_number} страница", callback_data="added2"),
            InlineKeyboardButton(text="->", callback_data=f"next_{current_page}" if current_page<page_number else "предел")
        ]

        keyboard.inline_keyboard.append(new_row)
        return keyboard







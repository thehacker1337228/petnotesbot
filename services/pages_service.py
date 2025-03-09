from services.note_service import NoteService
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import asyncio
from datetime import datetime


class PagesService:

    def __init__(self):
        self.note_service = NoteService()


    async def list(self,user_id):
        notes = self.note_service.get_all(user_id)
        titles = [(i.title, i.note_id) for i in reversed(notes)]
        return titles

    async def list_scope(self,user_id):
        notes = self.note_service.get_all(user_id)
        cnt = 0
        if not notes:
            scope = "У вас нет заметок"
            return scope
        else:
            scope = "=====[ Заметки ]=====\n"
            for note in reversed(notes):  # Разворачиваем порядок
                cnt+=1
                scope += f"<b>{note.title}</b> ({datetime.fromtimestamp(note.created_at).strftime('%d.%m.%y %H:%M')})\n{note.content}\n<i>ID: {cnt}</i>\n\n"
            return scope



    async def scope_slice(self, scope, current_page=1):
        MAX_LENGTH = 4096
        notes_list = scope.split("\n\n")
        notes_max = 10
        result_list = notes_list[notes_max*current_page-notes_max:notes_max*current_page]
        result = "\n\n".join(result_list)
        if len(result) <= MAX_LENGTH:
            return result
        else:
            return result[:MAX_LENGTH-3]+"..."






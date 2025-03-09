from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import math
import asyncio
from datetime import datetime

class ReplyKeyboards:


    # Определение кнопок
    ADD_KEY = "📌 Добавить заметку"
    LIST_KEY = "🗒️ Заметки скопом"
    INLINE_LIST_KEY = "📑 Список заметок"
    CANCEL_KEY = "Отменить"
    DELETE_KEY = "🗑️ Удалить заметку"

    # Создание клавиатуры
    main = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=ADD_KEY)],
        [KeyboardButton(text=INLINE_LIST_KEY), KeyboardButton(text=LIST_KEY)]
    ], resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


    cancel_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=CANCEL_KEY)]], resize_keyboard=True)
    delete_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=DELETE_KEY), KeyboardButton(text=CANCEL_KEY)]], resize_keyboard=True)


class InlineKeyboards:
    async def gen_inline(self,titles,current_page = 1, force = False, note_id = 0):
        page_max = 5 #максимальное количество заметок на странице
        cnt = 0
        head_row = None
        if force:
            page_max = 3
            head_row = [
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"del_{note_id}"),
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{note_id}")
            ]
            cnt = 1
        page_number = math.ceil(len(titles) / page_max)  # сколько всего страниц
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=f"📋 {title}", callback_data=f"note_{note_id}_{current_page}")] for title, note_id in titles[page_max*current_page-page_max:page_max*current_page]]
        )

        # Новый ряд кнопок
        footer_row = [
            InlineKeyboardButton(text="<-", callback_data=f"prev_{current_page}_{cnt}" if current_page>1 else "limit"),
            InlineKeyboardButton(text=f"{current_page}/{page_number} страница", callback_data="страница"),
            InlineKeyboardButton(text="->", callback_data=f"next_{current_page}_{cnt}" if current_page<page_number else "limit")
        ]

        # Добавляем новый ряд кнопок
        if head_row:
            keyboard.inline_keyboard.insert(0, head_row)
        keyboard.inline_keyboard.append(footer_row)
        return keyboard


    async def gen_inline_scope(self,scope, current_page=1):
        notes_max = 10 # максимальное количество заметок на странице
        page_number = math.ceil(scope.count("<b>") / notes_max)  # сколько всего страниц

        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        new_row = [
            InlineKeyboardButton(text="<-", callback_data=f"prv_{current_page}" if current_page>1 else "limit"),
            InlineKeyboardButton(text=f"{current_page}/{page_number} страница", callback_data="страница"),
            InlineKeyboardButton(text="->", callback_data=f"nxt_{current_page}" if current_page<page_number else "limit")
        ]

        keyboard.inline_keyboard.append(new_row)
        return keyboard

kb = ReplyKeyboards()
ikb = InlineKeyboards()

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Определение кнопок
ADD_KEY = "📌 Добавить"
LIST_KEY = "🗒️ Заметки скопом"
DEL_KEY = "❌ Удалить заметку"
EDIT_KEY = "✏️ Редактировать заметку"
INLINE_LIST_KEY = "📑 Список заметок"
CANCEL_KEY = "Отменить"

# Создание клавиатуры
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=ADD_KEY), KeyboardButton(text=LIST_KEY)],
    [KeyboardButton(text=DEL_KEY), KeyboardButton(text=EDIT_KEY)],
    [KeyboardButton(text=INLINE_LIST_KEY)]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


cancel_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=CANCEL_KEY)]], resize_keyboard=True)


buttons = ["Кнопка 1", "Кнопка 2", "Кнопка 3"]
keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text=btn, callback_data=btn)] for btn in buttons]
)

# Новый ряд кнопок
new_row = [
    InlineKeyboardButton(text="<-", callback_data="added1"),
    InlineKeyboardButton(text=f"{1} страница", callback_data="added2"),
    InlineKeyboardButton(text="->", callback_data="added3")
]

# Добавляем новый ряд кнопок
keyboard.inline_keyboard.append(new_row)
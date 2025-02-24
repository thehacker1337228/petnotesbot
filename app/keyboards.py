from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Определение кнопок
ADD_KEY = "📌 Добавить"
LIST_KEY = "🗒️ Мои заметки"
DEL_KEY = "❌ Удалить заметку"
EDIT_KEY = "✏️ Редактировать заметку"
START_KEY = "/start"
CANCEL_KEY = "Отменить"

# Создание клавиатуры
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text=ADD_KEY), KeyboardButton(text=LIST_KEY)],
    [KeyboardButton(text=DEL_KEY), KeyboardButton(text=EDIT_KEY)],
    [KeyboardButton(text=START_KEY)]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню...")


cancel_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=CANCEL_KEY)]], resize_keyboard=True)


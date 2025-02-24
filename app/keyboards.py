from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


#reply клава
main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Добавить"),
                                          KeyboardButton(text="Мои заметки")],
                                         [KeyboardButton(text="Удалить заметку"),
                                          KeyboardButton(text="Редактировать заметку")],
                                     [KeyboardButton(text="/start")]],
                               resize_keyboard=True,
                               input_field_placeholder="Выберите пункт меню...")

cancel_button = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Отменить")]], resize_keyboard=True)


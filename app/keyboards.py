from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Добавить"),
                                          KeyboardButton(text="Мои заметки")],
                                         [KeyboardButton(text="Удалить заметку"),
                                          KeyboardButton(text="Редактировать заметку")],
                                     [KeyboardButton(text="Главное меню")]],
                               resize_keyboard=True,
                               input_field_placeholder="Выберите пункт меню...")
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_markup(data):
    markup = InlineKeyboardBuilder()
    for i in data:
        markup.row(InlineKeyboardButton(text=i[0], callback_data=i[1]))
    return markup.as_markup()
from aiogram. types import (ReplyKeyboardMarkup, KeyboardButton,
                            InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Да', callback_data = 'YES'),
    InlineKeyboardButton(text= 'Нет', callback_data = 'NO')]
])


get_classes = ReplyKeyboardMarkup(keyboard = [
    [KeyboardButton(text='9')],
    [KeyboardButton(text='10')],
    [KeyboardButton(text='11')]

],  one_time_keyboard= True,
    input_field_placeholder='Выбери класс')


async def main_menu():
    keyboard = [
        [InlineKeyboardButton(text='📢 Ударения', callback_data=f'category_accents'),
        InlineKeyboardButton(text='✏️ Словарные слова', callback_data=f'category_dictionary')],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard )

async def button_categories(callback_data):
    keyboard = [
        [InlineKeyboardButton(text='🖍️ Ошибки', callback_data=f'error_{callback_data}'),
        InlineKeyboardButton(text='🚀 Начать', callback_data=f'start_{callback_data}')],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data=f"go_main")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
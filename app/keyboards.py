from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup,InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder,InlineKeyboardBuilder


main = InlineKeyboardMarkup(row_width=2,inline_keyboard=[
    [InlineKeyboardButton(text='Cоздать лабиринт',callback_data='create_maze',resize_keyboard=True),InlineKeyboardButton(text='Считать лабиринт из файла',callback_data='read_maze',resize_keyboard=True)]
    ])
async def second_part(msg_id):
    return InlineKeyboardMarkup(row_width=2,inline_keyboard=[
        [InlineKeyboardButton(text='Cоздать решение',callback_data='create_resh',resize_keyboard=True),InlineKeyboardButton(text='Сыграть',callback_data=f'play:{msg_id}',resize_keyboard=True)]
        ])

back = InlineKeyboardMarkup(row_width=2,inline_keyboard=[
    [InlineKeyboardButton(text='Назад',callback_data='main',resize_keyboard=True)]
    ])


game = InlineKeyboardMarkup(row_width=2,inline_keyboard=[
        [InlineKeyboardButton(text='Вверх',callback_data=f'up',resize_keyboard=True),InlineKeyboardButton(text='Вниз',callback_data=f'down',resize_keyboard=True)],
        [InlineKeyboardButton(text='Влево',callback_data=f'left',resize_keyboard=True),InlineKeyboardButton(text='Вправо',callback_data=f'right',resize_keyboard=True)],
        ])


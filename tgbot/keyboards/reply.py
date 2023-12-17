from enum import Enum
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyButtons(str, Enum):
    SEND_MENU = '🧾 Show Menu'


def user_menu_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(
        text=ReplyButtons.SEND_MENU
    )
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True)

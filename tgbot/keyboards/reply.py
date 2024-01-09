from enum import Enum
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyButtons(str, Enum):
    BTN_SEND_REPORT = '🧾 Отправить отчет'

class NavButtons(str, Enum):
    BTN_NEXT = '➡️ Дальше'
    BTN_BACK = '↩️ Назад'
    BTN_SEND = '➡️ Отправить'
    BTN_CANCEL = '❌ Отменить'



def user_menu_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(
        text=ReplyButtons.BTN_SEND_REPORT
    )
    keyboard.adjust(1)
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)

def nav_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(
        text=NavButtons.BTN_BACK
    )
    keyboard.button(
        text=NavButtons.BTN_CANCEL
    )
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True, input_field_placeholder='Введите ответ')

def z_report_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(
        text=NavButtons.BTN_BACK
    )
    keyboard.button(
        text=NavButtons.BTN_NEXT
    )
    keyboard.button(
        text=NavButtons.BTN_CANCEL
    )
    keyboard.adjust(2)
    return keyboard.as_markup(resize_keyboard=True, input_field_placeholder='Введите ответ')

def send_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(
        text=NavButtons.BTN_SEND
    )
    keyboard.button(
        text=NavButtons.BTN_BACK
    )
    keyboard.button(
        text=NavButtons.BTN_CANCEL
    )
    keyboard.adjust(1, 2)
    return keyboard.as_markup(resize_keyboard=True)

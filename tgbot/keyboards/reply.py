from enum import Enum
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyButtons(str, Enum):
    BTN_SEND_REPORT = "🧾 Отправить отчет"


class NavButtons(str, Enum):
    BTN_NEXT = "➡️ Дальше"
    BTN_BACK = "↩️ Назад"
    BTN_SEND = "➡️ Отправить"
    BTN_CANCEL = "❌ Отменить"


def user_menu_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=ReplyButtons.BTN_SEND_REPORT)
    keyboard.adjust()
    return keyboard.as_markup(
        input_field_placeholder=f"Нажмите на кнопку {ReplyButtons.BTN_SEND_REPORT.value}",
        one_time_keyboard=True,
        resize_keyboard=True
        )


def nav_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=NavButtons.BTN_BACK)
    keyboard.button(text=NavButtons.BTN_CANCEL)
    keyboard.adjust(2)
    return keyboard.as_markup(
        input_field_placeholder="Введите ответ...", resize_keyboard=True
    )


def excel_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=NavButtons.BTN_NEXT)
    keyboard.button(text=NavButtons.BTN_BACK)
    keyboard.button(text=NavButtons.BTN_CANCEL)
    keyboard.adjust(1, 2)
    return keyboard.as_markup(
        input_field_placeholder=f"Прикрепите фото Excel отчета. Чтобы заменить фото нажмите {NavButtons.BTN_BACK}",
        resize_keyboard=True,
    )


def send_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=NavButtons.BTN_SEND)
    keyboard.button(text=NavButtons.BTN_BACK)
    keyboard.button(text=NavButtons.BTN_CANCEL)
    keyboard.adjust(1, 2)
    return keyboard.as_markup(
        input_field_placeholder=f"Нажмите на кнопку {NavButtons.BTN_SEND.value}",
        resize_keyboard=True,
    )

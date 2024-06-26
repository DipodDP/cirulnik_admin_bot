from enum import Enum
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyButtons(str, Enum):
    BTN_SEND_REPORT = "🧾 Отправить отчет"
    BTN_UPDATE_USERS = "💇🏼‍♀️ Пользователи"
    BTN_UPDATE_LOCATIONS = "✂️ Добавить доступ к локации"
    BTN_DELETE_ACCESS = "❌ Удалить доступ к локации"


class NavButtons(str, Enum):
    BTN_NEXT = "➡️ Дальше"
    BTN_BACK = "↩️ Назад"
    BTN_SEND = "➡️ Отправить"
    BTN_CANCEL = "❌ Отменить"
    BTN_OK = "🆗"


def admin_users_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=ReplyButtons.BTN_DELETE_ACCESS)
    keyboard.button(text=NavButtons.BTN_CANCEL)
    keyboard.adjust()
    return keyboard.as_markup(
        input_field_placeholder=f"Нажмите на кнопку {ReplyButtons.BTN_SEND_REPORT.value}",
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def user_menu_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=ReplyButtons.BTN_SEND_REPORT)
    keyboard.adjust()
    return keyboard.as_markup(
        input_field_placeholder=f"Нажмите на кнопку {ReplyButtons.BTN_SEND_REPORT.value}",
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def admin_menu_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=ReplyButtons.BTN_SEND_REPORT)
    keyboard.button(text=ReplyButtons.BTN_UPDATE_LOCATIONS)
    keyboard.button(text=ReplyButtons.BTN_DELETE_ACCESS)
    keyboard.adjust(1)
    return keyboard.as_markup(
        input_field_placeholder=f"Нажмите на кнопку {ReplyButtons.BTN_SEND_REPORT.value}",
        one_time_keyboard=True,
        resize_keyboard=True,
    )


def cancel_keyboard():
    keyboard = ReplyKeyboardBuilder()
    keyboard.button(text=NavButtons.BTN_CANCEL)
    keyboard.adjust(1, 2)
    return keyboard.as_markup(
        input_field_placeholder=f"Нажмите {NavButtons.BTN_CANCEL.value} для отмены",
        resize_keyboard=True,
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

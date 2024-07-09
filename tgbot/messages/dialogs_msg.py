from enum import Enum


class UsersDialogsMessages(str, Enum):
    CHOOSE_ACTION = "Выберите действие:"
    USER_DELETION = "💇🏼‍♀️ Удаление пользователя"
    ACCESS_DELETING = "❌ Удаление доступа к локации"
    CHOOSE_USER = "Выберите пользователя:"
    CONTINUE = "Продолжить"
    CHOOSE_LOCATION = "Выберите локацию:"

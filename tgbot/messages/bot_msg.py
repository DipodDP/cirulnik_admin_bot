from enum import Enum


class BotMessages(str, Enum):
    START = "Bot is running and ready. Press /start"
    STOP = "Bot is stopped"

class EchoMessages(str, Enum):
    WRONG = "Неверная команда или сообщение.\nПопробуйте отправить снова или нажмите /start"

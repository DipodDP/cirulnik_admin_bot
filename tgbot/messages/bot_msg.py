from enum import Enum


class BotMessages(str, Enum):
    START = "Bot is running and ready. Press /start"
    STOP = "Bot is stopped"

class EchoMessages(str, Enum):
    WRONG = "Неверная команда или сообщение.\nПроверьте тип отправляемого сообщения (текст, фото...) и попробуйте отправить снова, или нажмите /start"

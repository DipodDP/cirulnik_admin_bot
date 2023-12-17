from enum import Enum


class BotMessages(str, Enum):
    START = "Bot is running and ready. Press /start"
    STOP = "Bot is stopped"

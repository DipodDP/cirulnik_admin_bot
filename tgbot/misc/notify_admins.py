from aiogram import Bot
from betterlogging import logging
from tgbot.messages.bot_msg import BotMessages

from tgbot.services import broadcaster


async def on_startup(bot: Bot, admin_ids: list[int]):
    try:
        await broadcaster.broadcast(bot, admin_ids, BotMessages.START)
    except Exception as err:
        logging.exception(err)


async def on_shutdown(bot: Bot, admin_ids: list[int]):
    try:
        await broadcaster.broadcast(bot, admin_ids, BotMessages.STOP)
    except Exception as err:
        logging.exception(err)

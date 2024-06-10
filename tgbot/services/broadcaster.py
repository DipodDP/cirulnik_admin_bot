import asyncio
import logging
from typing import Union

from aiogram import Bot
from aiogram import exceptions
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, Message
from aiogram.utils.media_group import MediaType


async def send_message(
    bot: Bot,
    user_id: Union[int, str],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: ParseMode | None = None,
    media: list[MediaType] = []
) -> bool:
    """
    Safe messages sender

    :param bot: Bot instance.
    :param user_id: user id. If str - must contain only digits.
    :param text: text of the message.
    :param disable_notification: disable notification or not.
    :param reply_markup: reply markup.
    :param media: list of media, only if sending meadiafile or album.
    :return: success.
    """

    try:
        if len(media) == 0:
            await bot.send_message(
                user_id,
                text,
                disable_notification=disable_notification,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        else:
            await bot.send_media_group(
                user_id,
                media,
                disable_notification=disable_notification,
            )
    except exceptions.TelegramBadRequest as e:
        logging.error(f"Telegram server says - {e}")
    except exceptions.TelegramForbiddenError:
        logging.error(f"Target [ID:{user_id}]: got TelegramForbiddenError")
    except exceptions.TelegramRetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.retry_after} seconds."
        )
        await asyncio.sleep(e.retry_after)
        return await send_message(
            bot, user_id, text, disable_notification, reply_markup, parse_mode, media
        )  # Recursive call
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success")
        return True
    return False


async def broadcast(
    bot: Bot,
    users: list[Union[str, int]],
    text: str,
    disable_notification: bool = False,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: ParseMode | None = None,
    media = []
) -> int:
    """
    Simple broadcaster.
    :param bot: Bot instance.
    :param users: List of users.
    :param text: Text of the message.
    :param disable_notification: Disable notification or not.
    :param reply_markup: Reply markup.
    :parse_mode: Parse mode, default is MARKDOWN_V2.
    :return: Count of messages.
    """

    logging.info(f"-------Report Content-------\nReport text:\n{text}\n----------\nReport media:\n{media}")

    count = 0
    try:
        for user_id in users:
            if await send_message(
                bot, user_id, text, disable_notification, reply_markup, parse_mode, media
            ):
                count += 1
            await asyncio.sleep(
                0.05
            )  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful sent.")

    return count


async def broadcast_messages_copies(
    users: list[Union[str, int]],
    messages: list[Message],
    disable_notification: bool = False,
) -> int:
    """
    Simple broadcaster.
    :param bot: Bot instance.
    :param users: List of users.
    :param message: Message.
    :param disable_notification: Disable notification or not.
    :return: Count of messages.
    """
    count = 0
    try:
        for user_id in users:
            for message in messages:
                if await message.send_copy(user_id, disable_notification=disable_notification):
                    count += 1
            await asyncio.sleep(
                0.05
            )  # 20 messages per second (Limit: 30 messages per second)
    finally:
        logging.info(f"{count} messages successful copied.")

    return count

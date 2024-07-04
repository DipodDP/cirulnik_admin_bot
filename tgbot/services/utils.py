from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError
from betterlogging import logging


logger = logging.getLogger(__name__)


async def delete_prev_message(state: FSMContext):
    user_data = await state.get_data()

    try:
        prev_bot_message: Message | None = user_data.get("prev_bot_message")
        await prev_bot_message.delete() if prev_bot_message is not None else ...
        keyboard_message: Message | None = user_data.get("keyboard_message")
        await keyboard_message.delete() if keyboard_message is not None else ...
    except TelegramAPIError as e:
        logger.exception(e.message)
    except KeyError:
        pass

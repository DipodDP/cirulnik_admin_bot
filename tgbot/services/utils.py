from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.exceptions import TelegramAPIError
from betterlogging import logging


logger = logging.getLogger(__name__)

async def delete_prev_message(state: FSMContext):
    user_data = await state.get_data()

    if 'prev_bot_message' in user_data:
        try:
            prev_bot_message: Message = user_data['prev_bot_message']
            logger.debug(prev_bot_message.message_id)
            await prev_bot_message.delete()
        except (TelegramAPIError) as e:
            logger.exception(e.message)

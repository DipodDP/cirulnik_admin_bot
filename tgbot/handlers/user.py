from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from betterlogging import logging
from tgbot.keyboards.reply import user_menu_keyboard

from tgbot.messages.handlers_msg import UserHandlerMessages


logger = logging.getLogger(__name__)

user_router = Router()

@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    user_data = await state.get_data()

    if 'prev_bot_message' in user_data:
        prev_bot_message: Message = user_data['prev_bot_message']
        await prev_bot_message.delete()

    answer = await message.answer(UserHandlerMessages.GREETINGS, reply_markup=user_menu_keyboard())
    await state.update_data(prev_bot_message=answer)
    await message.delete()
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')


@user_router.message(Command('help'))
async def help(message: Message, state: FSMContext):
    user_data = await state.get_data()

    if 'prev_bot_message' in user_data:
        prev_bot_message: Message = user_data['prev_bot_message']
        await prev_bot_message.delete()

    answer = await message.answer(UserHandlerMessages.HELP)
    await message.delete()
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

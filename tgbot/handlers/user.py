from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from betterlogging import logging
from tgbot.keyboards.reply import user_menu_keyboard

from tgbot.messages.handlers_msg import UserHandlerMessages
from tgbot.misc.states import CommonStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await delete_prev_message(state)
    
    if auth := await CommonStates().set_auth(state):
        answer = await message.answer(
            UserHandlerMessages.GREETINGS,
            reply_markup=user_menu_keyboard()
        )
    else:
        answer = await message.answer(UserHandlerMessages.AUTHORIZATION)

    state_data = await state.get_data()
    logger.info(' '.join([
        f'Logged user: @{state_data["author"] if "author" in state_data else None}',
        f'{message.from_user.username if message.from_user else None}',
        f'authorized: {auth}'
    ]))

    await message.delete()
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')


@user_router.message(Command('help'))
async def help(message: Message, state: FSMContext):
    await delete_prev_message(state)

    answer = await message.answer(UserHandlerMessages.HELP)
    await message.delete()
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

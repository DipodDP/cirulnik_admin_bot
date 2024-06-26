from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
)
from betterlogging import logging

# from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.owner import OwnerFilter
from tgbot.keyboards.reply import admin_menu_keyboard

from tgbot.messages.handlers_msg import UserHandlerMessages
from tgbot.misc.states import CommonStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

owner_router = Router()
owner_router.message.filter(OwnerFilter())
owner_router.callback_query.filter(OwnerFilter())


@owner_router.message(CommandStart())
@owner_router.message(StateFilter(None))
@owner_router.callback_query(StateFilter(None))
async def owner_start(
    event: Message | CallbackQuery, state: FSMContext, db_error: Exception | None = None
):
    if isinstance(event, Message):
        message = event
    else:
        message = event.message
    await delete_prev_message(state)

    await state.set_state(CommonStates.authorized)
    await state.update_data(
        author=event.from_user.username, author_name=event.from_user.full_name
    ) if event.from_user else ...

    if message and not isinstance(message, InaccessibleMessage):
        await message.delete()
        if db_error:
            answer = await message.answer(UserHandlerMessages.ERROR)

        else:
            answer = await message.answer(
                UserHandlerMessages.GREETINGS, reply_markup=admin_menu_keyboard()
            )

        await state.update_data(prev_bot_message=answer)
    logger.debug(f"{await state.get_state()}, {str(db_error)}")


@owner_router.message(Command("help"))
async def help(message: Message, state: FSMContext):
    await delete_prev_message(state)

    answer = await message.answer(UserHandlerMessages.HELP)
    await message.delete()
    await state.update_data(prev_bot_message=answer)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")

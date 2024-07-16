from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from betterlogging import logging

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.dialogs.states import UsersMenuStates
from tgbot.filters.admin import AdminFilter
from tgbot.filters.owner import OwnerFilter
from tgbot.keyboards.inline import (
    UserCallbackData,
    locations_keyboard,
    users_update_keyboard,
)
from tgbot.keyboards.reply import ReplyButtons, cancel_keyboard
from tgbot.messages.handlers_msg import DatabaseHandlerMessages
from tgbot.misc.states import AdminStates
from tgbot.services.utils import delete_prev_message

logger = logging.getLogger(__name__)

database_users_router = Router()
database_users_router.message.filter(AdminFilter() or OwnerFilter())
database_users_router.callback_query.filter(AdminFilter() or OwnerFilter())


@database_users_router.message(F.text.in_(ReplyButtons.BTN_UPDATE_LOCATIONS))
async def adding_location(
    message: Message,
    state: FSMContext,
    repo: RequestsRepo,
):
    await message.delete()
    await delete_prev_message(state)

    locations = await repo.locations.get_all_locations()

    # This method will send an answer to the message with the button, that user pressed
    # Here query - is a CallbackQuery object, which contains message: Message object
    if isinstance(message, Message):
        keyboard_message = await message.answer(
            DatabaseHandlerMessages.ADDING_LOCATION, reply_markup=cancel_keyboard()
        )
        answer = await message.answer(
            DatabaseHandlerMessages.CHOOSE_LOCATION,
            reply_markup=locations_keyboard(locations),
        )
    logger.info(f"Locations: {locations}")

    await state.set_state(AdminStates.updating_user_location)
    await state.update_data(
        keyboard_message=keyboard_message,
        prev_bot_message=answer,
    )

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@database_users_router.callback_query(
    AdminStates.updating_user_location, UserCallbackData.filter()
)
async def updating_location(
    query: CallbackQuery,
    callback_data: UserCallbackData,
    state: FSMContext,
    repo: RequestsRepo,
):
    users = await repo.users.get_all_users()

    if isinstance(query.message, Message):
        await query.message.edit_text(
            DatabaseHandlerMessages.CHOOSE_USER,
            reply_markup=users_update_keyboard(users, callback_data.location_id),
        )
    await state.set_state(AdminStates.adding_user_location)

    logger.info(f"Choosen location: {callback_data.location_id}, users: {users}")
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@database_users_router.message(F.text.in_(ReplyButtons.BTN_UPDATE_USERS))
async def updating_user(
    message: Message,
    state: FSMContext,
    dialog_manager: DialogManager,
):
    await message.delete()
    await delete_prev_message(state)

    await dialog_manager.start(UsersMenuStates.user_selection, mode=StartMode.RESET_STACK)

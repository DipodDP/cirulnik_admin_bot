from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_key_value, as_line, as_marked_list, as_section
from betterlogging import logging

from infrastructure.database.repo.requests import RequestsRepo
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
async def adding_location(message: Message, state: FSMContext, repo: RequestsRepo):
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


@database_users_router.message(F.text.in_(ReplyButtons.BTN_DELETE_ACCESS))
async def updating_user(message: Message, state: FSMContext, repo: RequestsRepo):
    await message.delete()
    await delete_prev_message(state)

    users = await repo.users.get_all_users()

    if isinstance(message, Message):
        keyboard_message = await message.answer(
            DatabaseHandlerMessages.DELETING_LOCATION, reply_markup=cancel_keyboard()
        )
        answer = await message.answer(
            DatabaseHandlerMessages.CHOOSE_USER,
            reply_markup=users_update_keyboard(users),
        )
    await state.set_state(AdminStates.updating_users)
    await state.update_data(
        keyboard_message=keyboard_message,
        prev_bot_message=answer,
    )
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@database_users_router.callback_query(
    AdminStates.updating_users, UserCallbackData.filter()
)
async def updating_user_location(
    query: CallbackQuery,
    callback_data: UserCallbackData,
    state: FSMContext,
    repo: RequestsRepo,
):
    await query.answer()

    logger.info(
        f"Updating user {callback_data.user_id}, location {callback_data.location_id}"
    )

    if isinstance(query.message, Message) and callback_data.user_id:
        user = await repo.users.get_user_by_id(callback_data.user_id)
        if user:
            try:
                locations = await repo.users.get_all_user_locations_relationships(
                    callback_data.user_id
                )
                text = as_section(
                    DatabaseHandlerMessages.UPDATING_USER.value,
                    as_marked_list(
                        as_key_value(
                            "Пользователь",
                            user.logged_as if user.logged_as else user.full_name,
                        ),
                        as_line("@", user.username),
                    ),
                )
                logger.debug(f"Choosen user: {text.as_kwargs()}")

                await query.message.edit_text(
                    text.as_markdown(),
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=locations_keyboard(locations, user.user_id),
                )
                await state.set_state(AdminStates.deleting_user_location)

            except Exception as e:
                logger.error(
                    f"Error updating users:\n {str(e)} \n{(await state.get_state())}"
                )
                await query.message.edit_text(
                    "\n".join([DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING, str(e)])
                )

        else:
            await query.message.edit_text("User not found!")

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")

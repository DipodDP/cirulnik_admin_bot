import json

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_key_value, as_marked_list, as_section
from betterlogging import logging

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import (
    UserCallbackData,
)
from tgbot.keyboards.reply import admin_menu_keyboard
from tgbot.messages.handlers_msg import DatabaseHandlerMessages, UserHandlerMessages
from tgbot.misc.states import AdminStates, CommonStates
from tgbot.services.utils import delete_prev_message

logger = logging.getLogger(__name__)

database_locations_router = Router()
database_locations_router.message.filter(AdminFilter())
database_locations_router.callback_query.filter(AdminFilter())


@database_locations_router.message(Command("loc"))
async def ask_for_update(message: Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    answer = await message.answer(DatabaseHandlerMessages.UPDATING_LOCATIONS)
    await state.set_state(AdminStates.updating_locations)
    await state.update_data(prev_bot_message=answer)


@database_locations_router.message(AdminStates.updating_locations)
async def update_locations(message: Message, state: FSMContext, repo: RequestsRepo):
    await message.delete()
    await delete_prev_message(state)

    count = 0
    errors = []
    if message.text:
        try:
            locations = json.loads(message.text)
            for location in locations:
                logger.info(f"Location: {location}")
                try:
                    await repo.locations.get_or_upsert_location(**location)
                    count += 1
                except Exception as e:
                    errors.append(e)
                    logger.error(
                        f"Error updating locations:\n {str(e)} \n{(await state.get_state())}"
                    )
        except Exception as e:
            errors.append(e)
            logger.error(
                f"Error JSON parsing:\n {str(e)} \n{(await state.get_state())}"
            )
    if message.text is None or errors:
        answer = await message.answer(
            "\n".join(
                [DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING]
                + [str(e) for e in errors],
            )
        )
    else:
        answer = await message.answer(
            DatabaseHandlerMessages.SUCCESSFUL_UPDATING + str(count)
        )

    await state.clear()
    await state.update_data(prev_bot_message=answer)

    state_data = await state.get_data()
    logger.debug(f"State data: {state_data}")
    logger.debug(f"{(await state.get_state())}")


# To filter the callback data, that was created with CallbackData factory, you can use .filter() method
@database_locations_router.callback_query(
    AdminStates.adding_user_location, UserCallbackData.filter()
)
async def add_location(
    query: CallbackQuery,
    callback_data: UserCallbackData,
    state: FSMContext,
    repo: RequestsRepo,
):
    # Firstly, always answer callback query (as Telegram API requires)
    await query.answer()

    logger.info(
        f"Adding to user {callback_data.user_id}, location {callback_data.location_id}"
    )

    if not callback_data.user_id or not callback_data.location_id:
        return

    # You can get the data from callback_data object as attributes
    location = await repo.locations.get_location_by_id(callback_data.location_id)

    if isinstance(query.message, Message):
        if location:
            try:
                await repo.users.add_user_location(
                    callback_data.user_id, callback_data.location_id
                )
                # Here we use aiogram.utils.formatting to format the text
                # https://docs.aiogram.dev/en/latest/utils/formatting.html
                text = as_section(
                    DatabaseHandlerMessages.SUCCESSFUL_UPDATING.value,
                    as_marked_list(
                        as_key_value("Филиал", location.location_name),
                        as_key_value("Адрес", location.address),
                    ),
                )
                logger.debug(f"Choosen location: {text.as_kwargs()}")

                await query.message.edit_text(
                    text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                logger.error(
                    f"Error updating locations:\n {str(e)} \n{(await state.get_state())}"
                )
                await query.message.edit_text(
                    "\n".join([DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING, str(e)])
                )

        else:
            await query.message.edit_text("Location not found!")

        state_data = await state.get_data()
        await CommonStates().check_auth(state)
        keyboard_message: Message | None = state_data.get('keyboard_message')
        await keyboard_message.delete() if keyboard_message is not None else ...
        keyboard_message = await query.message.answer(
            UserHandlerMessages.COMPLETED, reply_markup=admin_menu_keyboard()
        )
        await state.update_data(
            keyboard_message=keyboard_message, prev_bot_message=query.message
        )

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@database_locations_router.callback_query(
    AdminStates.deleting_user_location, UserCallbackData.filter()
)
async def del_location(
    query: CallbackQuery,
    callback_data: UserCallbackData,
    state: FSMContext,
    repo: RequestsRepo,
):
    await query.answer()

    logger.info(
        f"Deleting from user {callback_data.user_id}, location {callback_data.location_id}"
    )

    if not callback_data.user_id or not callback_data.location_id:
        return

    location = await repo.locations.get_location_by_id(callback_data.location_id)

    if isinstance(query.message, Message) and all(
        [callback_data.user_id, callback_data.location_id]
    ):
        if location:
            try:
                await repo.users.del_user_location(
                    callback_data.user_id, callback_data.location_id
                )
                text = as_section(
                    DatabaseHandlerMessages.SUCCESSFUL_UPDATING.value,
                    as_marked_list(
                        as_key_value("Филиал", location.location_name),
                        as_key_value("Адрес", location.address),
                    ),
                )
                logger.debug(f"Choosen location: {text.as_kwargs()}")

                await query.message.edit_text(
                    text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                logger.error(
                    f"Error updating locations:\n {str(e)} \n{(await state.get_state())}"
                )
                await query.message.edit_text(
                    "\n".join([DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING, str(e)])
                )

        else:
            await query.message.edit_text("Location not found!")

        state_data = await state.get_data()
        await CommonStates().check_auth(state)
        keyboard_message: Message | None = state_data.get('keyboard_message')
        await keyboard_message.delete() if keyboard_message is not None else ...
        keyboard_message = await query.message.answer(
            UserHandlerMessages.COMPLETED, reply_markup=admin_menu_keyboard()
        )
        await state.update_data(
            keyboard_message=keyboard_message, prev_bot_message=query.message
        )

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")

import json

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_key_value, as_marked_list, as_section
from betterlogging import logging

from infrastructure.database.models.users import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import LocationCallbackData, locations_update_keyboard
from tgbot.messages.handlers_msg import AdminHandlerMessages
from tgbot.misc.states import AdminStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

database_locations_router = Router()
database_locations_router.message.filter(AdminFilter())
database_locations_router.callback_query.filter(AdminFilter())


@database_locations_router.message(Command("loc"))
async def ask_for_update(message: Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    answer = await message.answer(AdminHandlerMessages.UPDATING_LOCATIONS)
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
                logger.debug(f"Location: {location}")
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
                [AdminHandlerMessages.UNSUCCESSFUL_UPDATING] + [str(e) for e in errors],
            )
        )
    else:
        answer = await message.answer(
            AdminHandlerMessages.SUCCESSFUL_UPDATING + str(count)
        )

    await state.clear()
    await state.update_data(prev_bot_message=answer)

    state_data = await state.get_data()
    logger.debug(f"State data: {state_data}")
    logger.debug(f"{(await state.get_state())}")


# We can use F.data filter to filter callback queries by data field from CallbackQuery object
# @database_locations_router.callback_query(F.data == "morning")
@database_locations_router.message(Command("add"))
async def adding_location(message: Message, state: FSMContext, repo: RequestsRepo):
    await message.delete()
    await delete_prev_message(state)

    locations = await repo.locations.get_all_locations()

    # This method will send an answer to the message with the button, that user pressed
    # Here query - is a CallbackQuery object, which contains message: Message object
    if isinstance(message, Message):
        await message.answer(
            AdminHandlerMessages.CHOOSE_LOCATION,
            reply_markup=locations_update_keyboard(locations),
        )
    await state.set_state(AdminStates.updating_user_location)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


# To filter the callback data, that was created with CallbackData factory, you can use .filter() method
@database_locations_router.callback_query(
    AdminStates.updating_user_location, LocationCallbackData.filter()
)
async def choose_location(
    query: CallbackQuery,
    callback_data: LocationCallbackData,
    state: FSMContext,
    user_from_db: User,
    repo: RequestsRepo,
):
    # Firstly, always answer callback query (as Telegram API requires)
    await query.answer()
    await delete_prev_message(state)

    # You can get the data from callback_data object as attributes
    location = await repo.locations.get_location_by_id(callback_data.location_id)

    if isinstance(query.message, Message):
        if location:
            try:
                await repo.users.add_user_location(
                    user_from_db.user_id, location.location_id
                )
                # Here we use aiogram.utils.formatting to format the text
                # https://docs.aiogram.dev/en/latest/utils/formatting.html
                text = as_section(
                    AdminHandlerMessages.SUCCESSFUL_UPDATING.value,
                    as_marked_list(
                        as_key_value("Филиал", location.location_name),
                        as_key_value("Адрес", location.address),
                    ),
                )
                logger.debug(f"Choosen location: {text.as_kwargs()}")

                answer = await query.message.answer(
                    text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                logger.error(
                    f"Error updating locations:\n {str(e)} \n{(await state.get_state())}"
                )
                answer = await query.message.answer(
                    "\n".join([AdminHandlerMessages.UNSUCCESSFUL_UPDATING, str(e)])
                )
            await query.message.delete()

        else:
            answer = await query.message.edit_text("Location not found!")

        await state.clear()
        await state.update_data(
            prev_bot_message=answer,
        )

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")

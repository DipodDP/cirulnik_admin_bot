from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import as_section, as_key_value, as_marked_list
from betterlogging import logging
from infrastructure.database.models.users import User
from infrastructure.database.repo.requests import RequestsRepo

from tgbot.handlers.user import user_start
from tgbot.keyboards.inline import (
    UserCallbackData,
    daytime_keyboard,
    locations_keyboard,
)
from tgbot.keyboards.reply import (
    NavButtons,
    ReplyButtons,
    admin_menu_keyboard,
    nav_keyboard,
    user_menu_keyboard,
    send_keyboard,
)
from tgbot.messages.handlers_msg import (
    DatabaseHandlerMessages,
    ReportClientsLost,
    ReportHandlerMessages,
    ReportMastersQuantity,
)
from tgbot.misc.report_to_owners import ReportBuilder, on_report
from tgbot.misc.states import CommonStates, ReportMenuStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_menu_router = Router()


@report_menu_router.message(
    F.text == ReplyButtons.BTN_SEND_REPORT, CommonStates.authorized
)
async def choose_daytime(message: Message, state: FSMContext, user_from_db: User):
    if user_from_db.username:
        await message.delete()
        await delete_prev_message(state)
        answer = await message.answer(
            ReportHandlerMessages.CHOOSE_DAYTIME, reply_markup=daytime_keyboard()
        )
        await state.set_state(ReportMenuStates.creating_report)
        await state.update_data(prev_bot_message=answer)

    else:
        await state.set_state(CommonStates.unauthorized)
        await user_start(message, state)

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


# We can use F.data filter to filter callback queries by data field from CallbackQuery object
@report_menu_router.callback_query(F.data == "morning")
async def choosed_morning(
    query: CallbackQuery, state: FSMContext, user_from_db: User, repo: RequestsRepo
):
    # Firstly, always answer callback query (as Telegram API requires)
    await query.answer()

    # This method will send an answer to the message with the button, that user pressed
    # Here query - is a CallbackQuery object, which contains message: Message object
    if isinstance(query.message, Message):
        locations = await repo.locations.get_all_locations()
        await query.message.edit_text(
            ReportHandlerMessages.CHOOSE_LOCATION,
            reply_markup=locations_keyboard(locations, user_from_db.user_id),
        )
        await state.update_data(daytime=query.data)
        await state.set_state(ReportMenuStates.choosing_location)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@report_menu_router.callback_query(F.data == "evening")
async def choosed_evening(
    query: CallbackQuery, state: FSMContext, user_from_db: User, repo: RequestsRepo
):
    await query.answer()
    if isinstance(query.message, Message):
        locations = await repo.locations.get_all_locations()
        await query.message.edit_text(
            ReportHandlerMessages.CHOOSE_LOCATION,
            reply_markup=locations_keyboard(locations, user_from_db.user_id),
        )
        await state.update_data(daytime=query.data)
        await state.set_state(ReportMenuStates.choosing_location)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


# To filter the callback data, that was created with CallbackData factory, you can use .filter() method
@report_menu_router.callback_query(UserCallbackData.filter())
async def choose_location(
    query: CallbackQuery,
    callback_data: UserCallbackData,
    state: FSMContext,
    repo: RequestsRepo,
):
    await query.answer()

    # You can get the data from callback_data object as attributes
    location_id = callback_data.location_id

    if isinstance(query.message, Message) and location_id:
        location = await repo.locations.get_location_by_id(location_id)

        if location:
            try:
                # Here we use aiogram.utils.formatting to format the text
                # https://docs.aiogram.dev/en/latest/utils/formatting.html
                text = as_section(
                    # as_key_value("Location #", location_info["id"]),
                    as_marked_list(
                        as_key_value("Филиал", location.location_name),
                        as_key_value("Адрес", location.address),
                    ),
                )
                logger.debug(f"Choosen location: {text.as_kwargs()}")

                location_message = await query.message.edit_text(
                    text.as_html(), parse_mode=ParseMode.HTML
                )
                await state.update_data(location=text)
                await state.update_data(location_id=location_id)
                await state.update_data(has_solarium=location.has_solarium)

                state_data = await state.get_data()

                if state_data["daytime"] == "morning":
                    answer_text = (
                        ReportHandlerMessages.MASTERS_QUANTITY
                        + ReportMastersQuantity.MALE
                    )
                    next_state = ReportMenuStates.entering_masters_quantity
                else:
                    answer_text = (
                        ReportHandlerMessages.CLIENTS_LOST + ReportClientsLost.MALE
                    )
                    next_state = ReportMenuStates.entering_clients_lost

                answer = await query.message.answer(
                    answer_text, reply_markup=nav_keyboard()
                )
                await state.set_state(next_state)

                await state.update_data(
                    prev_bot_message=answer,
                    location_message=location_message,
                )

                # You can also use MarkdownV2:
                # await query.message.edit_text(text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2)

            except Exception as e:
                logger.error(
                    f"Error updating users:\n {str(e)} \n{(await state.get_state())}"
                )
                await query.message.edit_text(
                    DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING
                )
        else:
            await query.message.edit_text("Location not found!")
            location_message = None

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@report_menu_router.message(F.photo, ReportMenuStates.uploading_solarium_counter)
async def upload_solarium_counter(
    message: types.Message,
    state: FSMContext,
    album: list[Message] | None = None,
):
    if album:
        [await message.delete() for message in album]
    else:
        await message.delete()
    await delete_prev_message(state)
    await state.update_data(solarium_counter=album if album else [message])

    state_data = await state.get_data()
    if state_data["daytime"] == "morning":
        await state.set_state(ReportMenuStates.completing_report)
        answer = await message.answer(
            ReportHandlerMessages.SEND_REPORT, reply_markup=send_keyboard()
        )

    elif state_data["daytime"] == "evening":
        await state.set_state(ReportMenuStates.uploading_z_report)
        answer = await message.answer(
            ReportHandlerMessages.Z_REPORT, reply_markup=nav_keyboard()
        )
    else:
        answer = None

    await state.update_data(prev_bot_message=answer)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@report_menu_router.message(
    F.text == NavButtons.BTN_SEND, ReportMenuStates.completing_report
)
async def complete_report(
    message: types.Message, state: FSMContext, user_from_db: User, repo: RequestsRepo
):
    await message.delete()
    await delete_prev_message(state)

    state_data = await state.get_data()
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")

    author, author_name = state_data["author"], state_data["author_name"]
    await state.clear()
    await state.update_data(author=author, author_name=author_name)
    await CommonStates().check_auth(state)

    location_id: int | None = state_data.get("location_id")
    users = await repo.users.get_users_by_location(location_id)

    if state_data["daytime"] == "morning":
        report = ReportBuilder(state_data)
        text = report.construct_morning_report()
        media = report.build_album()
        await on_report(message.bot, [user.user_id for user in users], text, media)

    elif state_data["daytime"] == "evening":
        report = ReportBuilder(state_data)
        text = report.construct_evening_report()
        media = report.build_album()
        await on_report(message.bot, [user.user_id for user in users], text, media)

    await message.answer(
        ReportHandlerMessages.REPORT_MORNING_COMPLETED
        if state_data["daytime"] == "morning"
        else ReportHandlerMessages.REPORT_EVENING_COMPLETED,
        reply_markup=admin_menu_keyboard()
        if user_from_db.is_owner
        else user_menu_keyboard(),
    )

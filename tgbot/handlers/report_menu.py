from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import as_section, as_key_value, as_marked_list
from betterlogging import logging
from tgbot.config import Config

from tgbot.keyboards.inline import daytime_keyboard, locations_keyboard, \
    LocationCallbackData
from tgbot.keyboards.reply import NavButtons, ReplyButtons, nav_keyboard, user_menu_keyboard
from tgbot.messages.handlers_msg import ReportClientsLost, ReportHandlerMessages, ReportMastersQuantity
from tgbot.misc.report_to_owners import ReportBuilder, on_report
from tgbot.misc.states import CommonStates, ReportMenuStates
from tgbot.services.broadcaster import broadcast_messages
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_menu_router = Router()


@report_menu_router.message(
    F.text == ReplyButtons.BTN_SEND_REPORT,
    CommonStates.authorized
)
async def choose_daytime(message: Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    answer = await message.answer(ReportHandlerMessages.CHOOSE_DAYTIME, reply_markup=daytime_keyboard())
    await state.set_state(ReportMenuStates.creating_report)
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')


# We can use F.data filter to filter callback queries by data field from CallbackQuery object
@report_menu_router.callback_query(F.data == "morning")
async def choosed_morning(query: CallbackQuery, state: FSMContext, config: Config):
    # Firstly, always answer callback query (as Telegram API requires)
    await query.answer()

    # This method will send an answer to the message with the button, that user pressed
    # Here query - is a CallbackQuery object, which contains message: Message object
    if query.message:
        await query.message.edit_text(
            ReportHandlerMessages.CHOOSE_LOCATION,
            reply_markup=locations_keyboard(config.misc.locations_list)
        )
        await state.update_data(daytime=query.data)
        await state.set_state(ReportMenuStates.choosing_location)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')


@report_menu_router.callback_query(F.data == "evening")
async def choosed_evening(query: CallbackQuery, state: FSMContext, config: Config):
    await query.answer()
    if query.message:
        await query.message.edit_text(
            ReportHandlerMessages.CHOOSE_LOCATION,
            reply_markup=locations_keyboard(config.misc.locations_list)
        )
        await state.update_data(daytime=query.data)
        await state.set_state(ReportMenuStates.choosing_location)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')


# To filter the callback data, that was created with CallbackData factory, you can use .filter() method
@report_menu_router.callback_query(LocationCallbackData.filter())
async def choose_location(
        query: CallbackQuery,
        callback_data: LocationCallbackData,
        state: FSMContext,
        config: Config
    ):
    await query.answer()

    # You can get the data from callback_data object as attributes
    location_id = callback_data.location_id

    # Then you can get the location from your database (here we use a simple list)
    location_info = next(
        (location for location in config.misc.locations_list if location["id"] == location_id), None)

    if query.message:
        if location_info:
            # Here we use aiogram.utils.formatting to format the text
            # https://docs.aiogram.dev/en/latest/utils/formatting.html
            text = as_section(
                # as_key_value("Location #", location_info["id"]),
                as_marked_list(
                    as_key_value("Филиал", location_info["title"]),
                    as_key_value("Адрес", location_info["address"]),
                ),
            )
            logger.debug(f'Choosen location: {text.as_kwargs()}')

            location_message = await query.message.edit_text(text.as_html(), parse_mode=ParseMode.HTML)
            await state.update_data(location=text)

            state_data = await state.get_data()

            if state_data['daytime'] == 'morning':
                answer_text = ReportHandlerMessages.MASTERS_QUANTITY + ReportMastersQuantity.MALE
                next_state = ReportMenuStates.entering_masters_quantity
            else:
                answer_text = ReportHandlerMessages.CLIENTS_LOST + ReportClientsLost.MALE
                next_state = ReportMenuStates.entering_clients_lost

            answer = await query.message.answer(answer_text,reply_markup=nav_keyboard())
            await state.set_state(next_state)

            # You can also use MarkdownV2:
            # await query.message.edit_text(text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2)
        else:
            answer = await query.message.edit_text("Location not found!")
            location_message = None

        await state.update_data(prev_bot_message=answer, location_message=location_message,)

    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

@report_menu_router.message(F.text == NavButtons.BTN_SEND, ReportMenuStates.completing_report)
async def complete_report(message: types.Message, state: FSMContext, config: Config):
    await message.delete()
    await delete_prev_message(state)

    state_data = await state.get_data() 
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

    author, author_name = state_data['author'], state_data['author_name']
    await state.clear()
    await state.update_data(author=author,author_name=author_name)
    await CommonStates().check_auth(state)

    await message.answer(
            ReportHandlerMessages.REPORT_EVENING_COMPLETED
                if ['daytime'] == 'morning'
                else ReportHandlerMessages.REPORT_MORNING_COMPLETED,
        reply_markup=user_menu_keyboard()
    )

    if state_data['daytime'] == 'morning':
        await on_report(message.bot, config.tg_bot.admin_ids, ReportBuilder(state_data).construct_morning_report())
        await broadcast_messages(config.tg_bot.admin_ids, state_data['open_check'])
    elif state_data['daytime'] == 'evening':
        await on_report(message.bot, config.tg_bot.admin_ids, ReportBuilder(state_data).construct_evening_report())
        await broadcast_messages(config.tg_bot.admin_ids, state_data['daily_excel'])
        await broadcast_messages(config.tg_bot.admin_ids, state_data['z_report'])

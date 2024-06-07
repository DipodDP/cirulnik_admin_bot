from aiogram import types, Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from betterlogging import logging

from tgbot.config import Config
from tgbot.handlers.report_menu import choose_daytime
from tgbot.handlers.report_morning import (
    enter_absent,
    enter_latecomers,
    enter_masters_quantity,
)
from tgbot.handlers.report_evening import (
    enter_clients_lost,
    enter_day_resume,
    enter_disgruntled_clients,
    enter_sbp_sum,
    enter_total_clients,
    upload_daily_excel,
    upload_z_report,
)

from tgbot.keyboards.reply import NavButtons, nav_keyboard, user_menu_keyboard
from tgbot.messages.handlers_msg import (
    ReportClientsLost,
    ReportHandlerMessages,
    ReportMastersQuantity,
)
from tgbot.misc.states import CommonStates, ReportMenuStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_nav_buttons_router = Router()


@report_nav_buttons_router.message(F.text.in_(NavButtons.BTN_BACK))
async def btn_back(message: types.Message, state: FSMContext, config: Config):
    state_data = await state.get_data()

    match current_state := await state.get_state():
        # Morning report
        case "ReportMenuStates:entering_masters_quantity":
            if "location_message" in state_data:
                location_message: types.Message = state_data["location_message"]
                await location_message.delete()
            await state.set_state(ReportMenuStates.choosing_location)
            await state.update_data(masters_quantity={})
            await choose_daytime(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:entering_latecomers":
            await message.delete()
            await delete_prev_message(state)
            await state.set_state(ReportMenuStates.entering_masters_quantity)
            await state.update_data(masters_quantity={})
            answer = await message.answer(
                ReportHandlerMessages.MASTERS_QUANTITY + ReportMastersQuantity.MALE,
                reply_markup=nav_keyboard(),
            )
            await state.update_data(prev_bot_message=answer)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:entering_absent":
            await state.set_state(ReportMenuStates.entering_masters_quantity)
            await enter_masters_quantity(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:uploading_open_check":
            await state.set_state(ReportMenuStates.entering_latecomers)
            await enter_latecomers(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        # Evening report
        case "ReportMenuStates:entering_clients_lost":
            data = await state.get_data()
            if "location_message" in data:
                location_message: types.Message = data["location_message"]
                await location_message.delete()
            await state.set_state(ReportMenuStates.choosing_location)
            await state.update_data(clients_lost={})
            await choose_daytime(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:entering_total_clients":
            await message.delete()
            await delete_prev_message(state)
            await state.set_state(ReportMenuStates.entering_clients_lost)
            await state.update_data(clients_lost={})
            answer = await message.answer(
                ReportHandlerMessages.CLIENTS_LOST + ReportClientsLost.MALE,
                reply_markup=nav_keyboard(),
            )
            await state.update_data(prev_bot_message=answer)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:uploading_daily_excel":
            await state.set_state(ReportMenuStates.entering_clients_lost)
            for msg in state_data["daily_excel"]:
                try:
                    await msg.delete()
                except TelegramBadRequest as e:
                    logger.warning(e.message)
            await state.update_data(daily_excel=[])
            await enter_clients_lost(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:uploading_z_report":
            await state.set_state(ReportMenuStates.entering_total_clients)
            await state.update_data(daily_excel=[])
            await enter_total_clients(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:entering_sbp_sum":
            await state.set_state(ReportMenuStates.uploading_daily_excel)
            await upload_daily_excel(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:entering_day_resume":
            await state.set_state(ReportMenuStates.uploading_z_report)
            await upload_z_report(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:entering_disgruntled_clients":
            await state.set_state(ReportMenuStates.entering_sbp_sum)
            await enter_sbp_sum(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:entering_argues_with_masters":
            await state.set_state(ReportMenuStates.entering_day_resume)
            await enter_day_resume(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        # Common states
        case "ReportMenuStates:uploading_solarium_counter":
            if state_data["daytime"] == "morning":
                logger.debug(f"Time of day: {state_data['daytime']}")
                await state.set_state(ReportMenuStates.uploading_open_check)
                await enter_absent(message, state)

            elif state_data["daytime"] == "evening":
                logger.debug(f"Time of day: {state_data['daytime']}")
                await state.set_state(ReportMenuStates.entering_total_clients)
                await enter_total_clients(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

        case "ReportMenuStates:completing_report":
            if state_data["daytime"] == "morning":
                logger.debug(f"Time of day: {state_data['daytime']}")
                await state.set_state(ReportMenuStates.entering_absent)
                await enter_absent(message, state)

            elif state_data["daytime"] == "evening":
                logger.debug(f"Time of day: {state_data['daytime']}")
                await state.set_state(ReportMenuStates.entering_disgruntled_clients)
                await enter_disgruntled_clients(message, state)
            logger.debug(f"Back to state: {await state.get_state()}")

    # Restoring data from previous step, except for some keys in state data
    state_data.pop("prev_bot_message") if "prev_bot_message" in state_data else ...
    state_data.pop("masters_quantity") if "masters_quantity" in state_data else ...
    state_data.pop("clients_lost") if "clients_lost" in state_data else ...
    state_data.pop("daily_excel") if "daily_excel" in state_data else ...
    await state.update_data(**state_data)
    logger.debug(f"Back from state: {current_state} to {await state.get_state()}")


@report_nav_buttons_router.message(F.text.in_(NavButtons.BTN_CANCEL))
async def btn_cancel(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    state_data = await state.get_data()
    await state.clear()
    if "location_message" in state_data:
        location_message: types.Message = state_data["location_message"]
        await location_message.delete()

    if "author" in state_data and "author_name" in state_data:
        author, author_name = state_data["author"], state_data["author_name"]
        await state.update_data(author=author, author_name=author_name)

    await CommonStates().check_auth(state)

    answer = await message.answer(
        ReportHandlerMessages.REPORT_CANCELED, reply_markup=user_menu_keyboard()
    )
    await state.update_data(prev_bot_message=answer)

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")

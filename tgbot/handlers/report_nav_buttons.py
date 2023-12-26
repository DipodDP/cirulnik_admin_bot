from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.context import FSMContext
from betterlogging import logging
from tgbot.handlers.report_menu import choose_daytime
from tgbot.handlers.report_morning import enter_absent, enter_latecomers, enter_masters_quantity
from tgbot.handlers.report_evening import enter_clients_lost, enter_day_resume, enter_disgruntled_clients, enter_sbp_sum, enter_total_clients, upload_daily_excel, upload_z_report

from tgbot.keyboards.reply import NavButtons, nav_keyboard, user_menu_keyboard
from tgbot.messages.handlers_msg import ReportHandlerMessages
from tgbot.misc.states import CommonStates, ReportMenuStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_nav_buttons_router = Router()

@report_nav_buttons_router.message(F.text.in_(NavButtons.BTN_BACK))
async def btn_back(message: types.Message, state: FSMContext):

    state_data = await state.get_data()

    match current_state := await state.get_state():

        # Morning report
        case 'ReportMenuStates:entering_masters_quantity':
            data = await state.get_data()
            if 'location_message' in data:
                location_message: types.Message = data['location_message']
                await location_message.delete()
            await state.set_state(ReportMenuStates.choosing_location)
            await choose_daytime(message, state)

        case 'ReportMenuStates:entering_latecomers':
            await message.delete()
            await delete_prev_message(state)
            await state.set_state(ReportMenuStates.entering_masters_quantity)
            answer = await message.answer(ReportHandlerMessages.MASTERS_QUANTITY,reply_markup=nav_keyboard())
            await state.update_data(prev_bot_message=answer)

        case 'ReportMenuStates:entering_absent':
            await state.set_state(ReportMenuStates.entering_masters_quantity)
            await enter_masters_quantity(message, state)

        case 'ReportMenuStates:uploading_open_check':
            await state.set_state(ReportMenuStates.entering_latecomers)
            await enter_latecomers(message, state)

        # Evening report
        case 'ReportMenuStates:entering_clients_lost':
            data = await state.get_data()
            if 'location_message' in data:
                location_message: types.Message = data['location_message']
                await location_message.delete()
            await state.set_state(ReportMenuStates.choosing_location)
            await choose_daytime(message, state)

        case 'ReportMenuStates:entering_total_clients':
            await message.delete()
            await delete_prev_message(state)
            await state.set_state(ReportMenuStates.entering_clients_lost)
            answer = await message.answer(ReportHandlerMessages.CLIENTS_LOST,reply_markup=nav_keyboard())
            await state.update_data(prev_bot_message=answer)

        case 'ReportMenuStates:uploading_daily_excel':
            await state.set_state(ReportMenuStates.entering_clients_lost)
            await enter_clients_lost(message, state)

        case 'ReportMenuStates:uploading_z_report':
            await state.set_state(ReportMenuStates.entering_total_clients)
            await enter_total_clients(message, state)

        case 'ReportMenuStates:entering_sbp_sum':
            await state.set_state(ReportMenuStates.uploading_daily_excel)
            await upload_daily_excel(message, state)

        case 'ReportMenuStates:entering_day_resume':
            await state.set_state(ReportMenuStates.uploading_z_report)
            await upload_z_report(message, state)

        case 'ReportMenuStates:entering_disgruntled_clients':
            await state.set_state(ReportMenuStates.entering_sbp_sum)
            await enter_sbp_sum(message, state)

        case 'ReportMenuStates:entering_argues_with_masters':
            await state.set_state(ReportMenuStates.entering_day_resume)
            await enter_day_resume(message, state)

        case 'ReportMenuStates:completing_report':
            if state_data['daytime'] == 'morning':
                await state.set_state(ReportMenuStates.entering_absent)
                await enter_absent(message, state)

            elif state_data['daytime'] == 'evening':
                await state.set_state(ReportMenuStates.entering_disgruntled_clients)
                await enter_disgruntled_clients(message, state)

    # Restoring data from previous step, except message to delete
    state_data.pop('prev_bot_message')
    await state.update_data(**state_data)
    logger.debug(f'{current_state}, {state_data}')


@report_nav_buttons_router.message(F.text.in_(NavButtons.BTN_CANCEL))
async def btn_cancel(message: types.Message, state: FSMContext):

    await message.delete()
    await delete_prev_message(state)
    state_data = await state.get_data()
    if 'location_message' in state_data:
        location_message: types.Message = state_data['location_message']
        await location_message.delete()

    author, author_name = state_data['author'], state_data['author_name']
    await state.clear()
    await state.update_data(author=author,author_name=author_name)
    await CommonStates().set_auth(state)

    answer = await message.answer(ReportHandlerMessages.REPORT_CANCELED,reply_markup=user_menu_keyboard())
    await state.update_data(prev_bot_message=answer)

    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

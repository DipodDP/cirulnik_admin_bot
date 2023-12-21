
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.context import FSMContext
from betterlogging import logging
from tgbot.handlers.report_menu import choose_daytime
from tgbot.handlers.report_morning import enter_latecomers, enter_masters_quantity

from tgbot.keyboards.reply import NavButtons, nav_keyboard, user_menu_keyboard
from tgbot.messages.handlers_msg import ReportHandlerMessages
from tgbot.misc.states import ReportMenuStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_nav_buttons_router = Router()

@report_nav_buttons_router.message(F.text.in_(NavButtons.BTN_BACK))
async def btn_back(message: types.Message, state: FSMContext):

    match await state.get_state():
        case 'ReportMenuStates:entering_masters_quantity':
            await delete_prev_message(state)
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

        case 'ReportMenuStates:completing_report':
            await state.set_state(ReportMenuStates.entering_latecomers)
            await enter_latecomers(message, state)

    logger.debug(f'{await state.get_state()}, {await state.get_data()}')


@report_nav_buttons_router.message(F.text.in_(NavButtons.BTN_CANCEL))
async def btn_cancel(message: types.Message, state: FSMContext):

    await message.delete()
    await delete_prev_message(state)
    data = await state.get_data()
    if 'location_message' in data:
        location_message: types.Message = data['location_message']
        await location_message.delete()
    await state.clear()
    answer = await message.answer(ReportHandlerMessages.REPORT_CANCELED,reply_markup=user_menu_keyboard())
    await state.update_data(prev_bot_message=answer)

    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

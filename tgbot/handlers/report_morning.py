from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from betterlogging import logging

from tgbot.keyboards.reply import nav_keyboard, send_keyboard
from tgbot.messages.handlers_msg import ReportHandlerMessages
from tgbot.misc.states import ReportMenuStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_morning_router = Router()

@report_morning_router.message(ReportMenuStates.entering_masters_quantity)
async def enter_masters_quantity(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(masters_quantity=message.text)
    await state.set_state(ReportMenuStates.entering_latecomers)
    answer = await message.answer(ReportHandlerMessages.LATECOMERS, reply_markup=nav_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

@report_morning_router.message(ReportMenuStates.entering_latecomers)
async def enter_latecomers(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(latecomers=message.text)
    await state.set_state(ReportMenuStates.entering_absent)
    answer = await message.answer(ReportHandlerMessages.ABSENT, reply_markup=nav_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {(await state.get_data())}')

@report_morning_router.message(ReportMenuStates.entering_absent)
async def enter_absent(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(absent=message.text)
    await state.set_state(ReportMenuStates.uploading_open_check)
    answer = await message.answer(ReportHandlerMessages.OPEN_CHECK,reply_markup=nav_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

# To get high quality photo from message: F.photo[-1].as_('largest_photo')
@report_morning_router.message(F.photo, ReportMenuStates.uploading_open_check)
async def upload_open_reciept(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(open_check=message)
    await state.set_state(ReportMenuStates.completing_report)
    answer = await message.answer(ReportHandlerMessages.SEND_REPORT,reply_markup=send_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types.message import Message
from betterlogging import logging

from tgbot.keyboards.reply import nav_keyboard, send_keyboard
from tgbot.messages.handlers_msg import ReportHandlerMessages, ReportMastersQuantity
from tgbot.misc.states import ReportMenuStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_morning_router = Router()

@report_morning_router.message(ReportMenuStates.entering_masters_quantity)
async def enter_masters_quantity(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)

    state_data = await state.get_data()
    masters_quantity = state_data['masters_quantity'] if 'masters_quantity' in state_data else {}
    list_of_masters_types = list(ReportMastersQuantity)

    for i, item in enumerate(list_of_masters_types):
        if item.value not in masters_quantity:
            masters_quantity.update({item.value: message.text})
            await state.update_data(masters_quantity=masters_quantity)

            if i+1 < len(list_of_masters_types):
                answer = await message.answer(
                    ReportHandlerMessages.MASTERS_QUANTITY +
                    list_of_masters_types[i+1],
                    reply_markup=nav_keyboard()
                )
                await state.update_data(prev_bot_message=answer)

                break
    else:
        await state.set_state(ReportMenuStates.entering_latecomers)
        answer = await message.answer(ReportHandlerMessages.LATECOMERS, reply_markup=nav_keyboard())
        await state.update_data(prev_bot_message=answer)

    state_data = await state.get_data()
    logger.debug(f"Masters quantity: {state_data['masters_quantity']}" if 'masters_quantity' in state_data else None)
    logger.debug(f'{(await state.get_state())}')

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
async def upload_open_reciept(
        message: types.Message,
        state: FSMContext,
        album: list[Message] | None = None
    ):
    if album:
        [await message.delete() for message in album]
    else:
        await message.delete()
    await delete_prev_message(state)
    await state.update_data(open_check=album if album else [message])
    await state.set_state(ReportMenuStates.completing_report)
    answer = await message.answer(ReportHandlerMessages.SEND_REPORT,reply_markup=send_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

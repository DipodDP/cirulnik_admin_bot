from aiogram import F, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types.message import Message
from betterlogging import logging

from tgbot.keyboards.reply import NavButtons, nav_keyboard, send_keyboard, z_report_keyboard
from tgbot.messages.handlers_msg import ReportClientsLost, ReportHandlerMessages
from tgbot.misc.states import ReportMenuStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

report_evening_router = Router()

@report_evening_router.message(ReportMenuStates.entering_clients_lost)
async def enter_clients_lost(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)

    state_data = await state.get_data()
    clients_lost = state_data['clients_lost'] if 'clients_lost' in state_data else {}
    list_of_masters_types = list(ReportClientsLost)

    for i, item in enumerate(list_of_masters_types):
        if item.value not in clients_lost:
            clients_lost.update({item.value: message.text})
            await state.update_data(clients_lost=clients_lost)

            if i+1 < len(list_of_masters_types):
                answer = await message.answer(
                    ReportHandlerMessages.CLIENTS_LOST +
                    list_of_masters_types[i+1],
                    reply_markup=nav_keyboard()
                )
                await state.update_data(prev_bot_message=answer)

                break
    else:
        await state.set_state(ReportMenuStates.entering_total_clients)
        answer = await message.answer(ReportHandlerMessages.TOTAL_CLIENTS, reply_markup=nav_keyboard())
        await state.update_data(prev_bot_message=answer)

    state_data = await state.get_data()
    logger.debug(f"Clients lost: {state_data['clients_lost']}" if 'clients_lost' in state_data else None)
    logger.debug(f'{(await state.get_state())}')

@report_evening_router.message(ReportMenuStates.entering_total_clients)
async def enter_total_clients(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(total_clients=message.text)
    await state.set_state(ReportMenuStates.uploading_daily_excel)
    answer = await message.answer(ReportHandlerMessages.DAILY_EXCEL, reply_markup=nav_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {(await state.get_data())}')

@report_evening_router.message(F.photo, ReportMenuStates.uploading_daily_excel)
async def upload_daily_excel(
        message: types.Message,
        state: FSMContext,
        album: list[Message] | None = None
    ):
    if album:
        [await message.delete() for message in album]
    else:
        await message.delete()
    await delete_prev_message(state)
    await state.update_data(daily_excel=album if album else [message])
    await state.set_state(ReportMenuStates.uploading_z_report)
    answer = await message.answer(
        ReportHandlerMessages.Z_REPORT,
        reply_markup=z_report_keyboard()
    )
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')

@report_evening_router.message(
    F.photo | F.text.in_(NavButtons.BTN_NEXT),
    ReportMenuStates.uploading_z_report
)
async def upload_z_report(
        message: types.Message,
        state: FSMContext,
        album: list[Message] | None = None
    ):
    state_data = await state.get_data()
    z_report_photos: list = state_data['z_report'] if 'z_report' in state_data else []
    logger.debug(f'{await state.get_state()}, z_report photos: {len(z_report_photos)}')

    if message.text == NavButtons.BTN_NEXT and len(z_report_photos) > 1:
        await delete_prev_message(state)
        if album:
            [await message.delete() for message in album]
        else:
            await message.delete()
        await state.set_state(ReportMenuStates.entering_sbp_sum)
        answer = await message.answer(ReportHandlerMessages.SBP_SUM, reply_markup=nav_keyboard())
        await state.update_data(prev_bot_message=answer)
        logger.debug(f'{await state.get_state()}, {await state.get_data()}')

    else:
        for msg in album if album else [message]:
            await msg.delete()
            if msg.photo: z_report_photos.append(msg)

        await state.update_data(z_report=z_report_photos)

@report_evening_router.message(ReportMenuStates.entering_sbp_sum)
async def enter_sbp_sum(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(sbp_sum=message.text)
    await state.set_state(ReportMenuStates.entering_day_resume)
    answer = await message.answer(ReportHandlerMessages.DAY_RESUME, reply_markup=nav_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {(await state.get_data())}')

@report_evening_router.message(ReportMenuStates.entering_day_resume)
async def enter_day_resume(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(day_resume=message.text)
    await state.set_state(ReportMenuStates.entering_disgruntled_clients)
    answer = await message.answer(ReportHandlerMessages.DISGRUNTLED_CLIENTS, reply_markup=nav_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {(await state.get_data())}')

@report_evening_router.message(ReportMenuStates.entering_disgruntled_clients)
async def enter_disgruntled_clients(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(disgruntled_clients=message.text)
    await state.set_state(ReportMenuStates.entering_argues_with_masters)
    answer = await message.answer(ReportHandlerMessages.ARGUES_WITH_MASTERS, reply_markup=nav_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {(await state.get_data())}')

@report_evening_router.message(ReportMenuStates.entering_argues_with_masters)
async def enter_argues_with_masters(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await state.update_data(argues_with_masters=message.text)
    await state.set_state(ReportMenuStates.completing_report)
    answer = await message.answer(ReportHandlerMessages.SEND_REPORT, reply_markup=send_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {(await state.get_data())}')

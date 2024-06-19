import json

from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from betterlogging import logging

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.reply import user_menu_keyboard
from tgbot.messages.handlers_msg import AdminHandlerMessages
from tgbot.misc.states import AdminStates, CommonStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())


@admin_router.message(CommandStart())
@admin_router.message(StateFilter(None))
@admin_router.callback_query(StateFilter(None))
async def admin_start(event: Message | CallbackQuery, state: FSMContext):
    if isinstance(event, Message):
        message = event
    else:
        message = event.message
    await delete_prev_message(state)

    await state.set_state(CommonStates.authorized)
    await state.update_data(
        author=event.from_user.username, author_name=event.from_user.full_name
    ) if event.from_user else ...

    if message and not isinstance(message, InaccessibleMessage):
        await message.delete()
        answer = await message.answer(
            AdminHandlerMessages.GREETINGS, reply_markup=user_menu_keyboard()
        )
        await state.update_data(prev_bot_message=answer)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@admin_router.message(Command("stop"))
async def stop_bot(message: Message):
    await message.answer(AdminHandlerMessages.STOPPING)
    await message.delete()
    exit()


@admin_router.message(Command("loc"))
async def ask_for_update(message: Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    answer = await message.answer(AdminHandlerMessages.UPDATING_LOCATIONS)
    await state.set_state(AdminStates.updating_location)
    await state.update_data(prev_bot_message=answer)


@admin_router.message(AdminStates.updating_location)
async def update_locations(message: Message, state: FSMContext, repo: RequestsRepo):
    await message.delete()
    await delete_prev_message(state)
    state_data = await state.get_data()

    count = 0
    errors = []
    if message.text:
        locations = json.loads(message.text)
        for location in locations:
            logger.debug(f"Location: {location}")
            try:
                await repo.locations.get_or_upsert_location(**location)
                count += 1
            except Exception as e:
                errors.append(e)
                logger.error(
                    f"Error updating locations:/n {str(e)} /n{(await state.get_state())}"
                )
    if message.text is None or errors:
        answer = await message.answer(
            "/n".join(
                [AdminHandlerMessages.UNSUCCESSFUL_UPDATING] + [str(e) for e in errors],
            )
        )
    else:
        answer = await message.answer(
            AdminHandlerMessages.SUCCESSFUL_UPDATING + str(count)
        )

    await state.clear()
    await state.update_data(prev_bot_message=answer)

    logger.debug(f"State data: {state_data}")
    logger.debug(f"{(await state.get_state())}")

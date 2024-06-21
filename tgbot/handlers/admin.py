from aiogram import Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, Message
from betterlogging import logging

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.reply import user_menu_keyboard
from tgbot.messages.handlers_msg import AdminHandlerMessages
from tgbot.misc.states import CommonStates
from tgbot.services.utils import delete_prev_message

logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.filter(AdminFilter())
admin_router.callback_query.filter(AdminFilter())


@admin_router.message(CommandStart())
@admin_router.message(StateFilter(None))
@admin_router.callback_query(StateFilter(None))
async def admin_start(
    event: Message | CallbackQuery, state: FSMContext, db_error: Exception | None = None
):
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
        if db_error:
            answer = await message.answer(
                "\n".join([AdminHandlerMessages.ERROR, "Database:", str(db_error)])
            )

        else:
            answer = await message.answer(
                AdminHandlerMessages.GREETINGS, reply_markup=user_menu_keyboard()
            )

        await state.update_data(prev_bot_message=answer)
    logger.debug(f"{await state.get_state()}, {str(db_error)}")


@admin_router.message(Command("stop"))
async def stop_bot(message: Message):
    await message.answer(AdminHandlerMessages.STOPPING)
    await message.delete()
    exit()

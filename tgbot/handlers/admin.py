from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from betterlogging import logging

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.reply import user_menu_keyboard
from tgbot.messages.handlers_msg import AdminHandlerMessages
from tgbot.misc.states import CommonStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

admin_router = Router()
admin_router.message.filter(AdminFilter())

@admin_router.message(CommandStart())
async def admin_start(message: Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)

    await state.set_state(CommonStates.authorized)
    await state.update_data(
        author=message.from_user.username,
        author_name=message.from_user.full_name
    ) if message.from_user else ...

    answer = await message.answer(AdminHandlerMessages.GREETINGS, reply_markup=user_menu_keyboard())
    await state.update_data(prev_bot_message=answer)
    logger.debug(f'{await state.get_state()}, {await state.get_data()}')


@admin_router.message(Command('stop'))
async def stop_bot(message: Message):
    await message.reply(AdminHandlerMessages.STOPPING)
    await message.delete()
    exit()

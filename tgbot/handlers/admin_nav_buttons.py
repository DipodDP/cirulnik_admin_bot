from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from betterlogging import logging

from tgbot.filters.admin import AdminFilter
from tgbot.filters.owner import OwnerFilter
from tgbot.keyboards.reply import NavButtons, admin_menu_keyboard
from tgbot.messages.handlers_msg import UserHandlerMessages
from tgbot.misc.states import CommonStates
from tgbot.services.utils import delete_location_message, delete_prev_message

logger = logging.getLogger(__name__)

admin_nav_buttons_router = Router()
admin_nav_buttons_router.message.filter(AdminFilter() or OwnerFilter())


@admin_nav_buttons_router.message(F.text.in_(NavButtons.BTN_CANCEL))
async def btn_cancel(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    await delete_location_message(state)
    state_data = await state.get_data()
    await state.clear()

    await state.update_data(
        author=state_data.get("author"), author_name=state_data.get("author_name")
    )

    await CommonStates().check_auth(state)

    answer = await message.answer(
        UserHandlerMessages.CANCEL, reply_markup=admin_menu_keyboard()
    )
    await state.update_data(prev_bot_message=answer)

    logger.debug(f"Back from state: {state} to {await state.get_state()}")

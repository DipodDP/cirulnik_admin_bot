from aiogram import types, Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hcode

from tgbot.filters.admin import AdminFilter
from tgbot.messages.bot_msg import EchoMessages
from tgbot.services.utils import delete_prev_message


echo_router = Router()


@echo_router.message(F.text, StateFilter(None), AdminFilter())
async def bot_echo_admin(message: types.Message):
    text = ["Echo without state", "Message:", message.text]
    await message.answer("\n".join(text))


@echo_router.message(F.text, AdminFilter())
async def bot_echo_all_admin(message: types.Message, state: FSMContext):
    state_name = await state.get_state()
    text = [
        f"Echo from state {hcode(state_name)}",
        "Message text:",
        hcode(message.text),
    ]
    await message.answer("\n".join(text))


@echo_router.message()
async def bot_echo(message: types.Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)
    text = [EchoMessages.WRONG, "Message:", message.text]
    answer = await message.answer("\n".join(text))
    await state.update_data(prev_bot_message=answer)

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from betterlogging import logging
from tgbot.keyboards.reply import user_menu_keyboard

from tgbot.messages.handlers_msg import UserHandlerMessages
from tgbot.misc.states import CommonStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
async def user_start(message: Message, state: FSMContext):
    await message.delete() if message is not None else ...
    await delete_prev_message(state)

    state_data = await state.get_data()
    location_message: Message | None = state_data.get("location_message")
    if location_message:
        await location_message.delete()

    if auth := await CommonStates().check_auth(state):
        answer = await message.answer(
            UserHandlerMessages.GREETINGS.format(user=state_data["author_name"]),
            reply_markup=user_menu_keyboard(),
        )
    else:
        # Checking if user has username
        if user := message.from_user:
            if user.username:
                answer = await message.answer(
                    UserHandlerMessages.AUTHORIZATION,
                    reply_markup=ReplyKeyboardRemove(),
                )

            else:
                answer = await message.answer(
                    UserHandlerMessages.ASK_USERNAME, reply_markup=ReplyKeyboardRemove()
                )
                await state.clear()
        else:
            answer = None

    await state.update_data(prev_bot_message=answer)

    logger.info(
        " ".join(
            [
                f'Logged user: @{state_data["author"] if "author" in state_data else None}',
                f"{message.from_user.username if message.from_user else None}",
                f"authorized: {auth}",
            ]
        )
    )

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@user_router.message(Command("help"))
async def help(message: Message, state: FSMContext):
    await delete_prev_message(state)

    answer = await message.answer(UserHandlerMessages.HELP)
    await message.delete()
    await state.update_data(prev_bot_message=answer)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@user_router.message(CommonStates.unauthorized)
async def user_auth(message: Message, state: FSMContext):
    await message.delete()
    await delete_prev_message(state)

    # Saving user info to state
    if user := message.from_user:
        author = (user.username if user.username else "N/A",)
        answer = await message.answer(
            UserHandlerMessages.GREETINGS.format(user=message.text),
            reply_markup=user_menu_keyboard(),
        )
        await state.update_data(prev_bot_message=answer)

    else:
        author = None

    await state.update_data(author=author)
    await state.update_data(author_name=message.text)
    await state.set_state(CommonStates.authorized)
    logger.info(f"Logged user: @{author} as {message.text}")

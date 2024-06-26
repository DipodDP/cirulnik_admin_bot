from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from betterlogging import logging
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.keyboards.reply import user_menu_keyboard

from tgbot.messages.handlers_msg import UserHandlerMessages
from tgbot.misc.states import CommonStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

user_router = Router()


@user_router.message(CommandStart())
async def user_start(
    message: Message,
    state: FSMContext,
    db_error: Exception | None = None,
):
    await message.delete() if message is not None else ...
    await delete_prev_message(state)

    if message.text:
        await state.update_data(author=None)
        await state.update_data(author_name=None)

    state_data = await state.get_data()
    location_message: Message | None = state_data.get("location_message")
    if location_message:
        await location_message.delete()

    if auth := await CommonStates().check_auth(state):
        logger.info(f'Auth for {state_data.get("author_name")} has been passed')
        answer = await message.answer(
            UserHandlerMessages.GREETINGS.format(user=state_data["author_name"]),
            reply_markup=user_menu_keyboard(),
        )

    else:
        logger.info(f'Auth for {state_data.get("author_name")} has been rejected')

        if db_error:
            answer = await message.answer(UserHandlerMessages.ERROR)
            logger.info(f"DB error! {db_error}")
            await state.clear()
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
                        UserHandlerMessages.ASK_USERNAME,
                        reply_markup=ReplyKeyboardRemove(),
                    )
                    await state.clear()
            else:
                answer = None

    await state.update_data(prev_bot_message=answer)

    logger.info(
        " ".join(
            [
                f'Logged user: @{state_data.get("author")}',
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
async def user_auth(message: Message, state: FSMContext, repo: RequestsRepo):
    await message.delete()
    await delete_prev_message(state)

    # Saving user info to DB
    if user := message.from_user:
        author = user.username if user.username else "N/A"
        answer = await message.answer(
            UserHandlerMessages.GREETINGS.format(user=message.text),
            reply_markup=user_menu_keyboard(),
        )
        await state.update_data(prev_bot_message=answer)
        await state.update_data(author_name=message.text)

        user_id = message.from_user.id
        result = await repo.users.set_user_logged_as(user_id, message.text)
        logger.info(f"Update in users table: {result}")

    else:
        author = None

    await state.update_data(author=author)
    await state.set_state(CommonStates.authorized)
    logger.info(f"Logged user: @{author} as {message.text}")

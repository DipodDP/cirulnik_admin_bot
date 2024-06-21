from datetime import datetime
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.message import Message
from betterlogging import logging

from infrastructure.database.models.users import User

from tgbot.handlers.user import user_start


logger = logging.getLogger(__name__)

auth_router = Router()


@auth_router.message(StateFilter(None))
@auth_router.callback_query(StateFilter(None))
async def non_auth_message(
    event: Message | CallbackQuery,
    state: FSMContext,
    user_from_db: User | None = None,
    db_error: Exception | None = None,
):
    if event.from_user:
        logger.info(f"User from DB: { user_from_db }")
    if user_from_db:
        await state.update_data(author=user_from_db.username)
        await state.update_data(author_name=user_from_db.logged_as)
        text = user_from_db.logged_as
    else:
        text = None

    if isinstance(event, CallbackQuery):
        if event.message:
            message = Message(
                message_id=event.message.message_id,
                date=datetime.now(),
                chat=event.message.chat,
                text=text,
                from_user=event.from_user,
            ).as_(event.bot)
        else:
            message = None
    else:
        message = Message(
            message_id=event.message_id,
            from_user=event.from_user,
            date=datetime.now(),
            chat=event.chat,
            text=text,
        ).as_(event.bot)
    await user_start(message, state, db_error)

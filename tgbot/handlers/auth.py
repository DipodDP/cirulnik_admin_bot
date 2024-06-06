from aiogram import types, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from betterlogging import logging

from infrastructure.database.models.users import User  as UserFromDB

# from infrastructure.database.repo.requests import RequestsRepo
from tgbot.handlers.user import user_auth


logger = logging.getLogger(__name__)

auth_router = Router()


@auth_router.message(StateFilter(None))
async def reset_auth(
    message: types.Message,
    state: FSMContext,
    # repo: RequestsRepo,
    user_from_db: UserFromDB
,
):
    # await message.delete()
    if message.from_user:
        logger.info(f'User from DB: { user_from_db }')
    await state.update_data(author=user_from_db.username)
    await state.update_data(author_name=user_from_db.full_name)
    await user_auth(message, state)

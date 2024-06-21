import json

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_key_value, as_line, as_marked_list, as_section
from betterlogging import logging

from infrastructure.database.models.users import User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.inline import UserCallbackData, users_update_keyboard
from tgbot.messages.handlers_msg import AdminHandlerMessages
from tgbot.misc.states import AdminStates
from tgbot.services.utils import delete_prev_message


logger = logging.getLogger(__name__)

database_users_router = Router()
database_users_router.message.filter(AdminFilter())
database_users_router.callback_query.filter(AdminFilter())


@database_users_router.message(Command("user"))
async def adding_user(message: Message, state: FSMContext, repo: RequestsRepo):
    await message.delete()
    await delete_prev_message(state)

    users = await repo.users.get_all_users()

    if isinstance(message, Message):
        await message.answer(
            AdminHandlerMessages.CHOOSE_USER,
            reply_markup=users_update_keyboard(users),
        )
    await state.set_state(AdminStates.updating_users)
    logger.debug(f"{await state.get_state()}, {await state.get_data()}")


@database_users_router.callback_query(
    AdminStates.updating_users, UserCallbackData.filter()
)
async def choose_user(
    query: CallbackQuery,
    callback_data: UserCallbackData,
    state: FSMContext,
    user_from_db: User,
    repo: RequestsRepo,
):
    await query.answer()
    await delete_prev_message(state)

    user = await repo.users.get_user_by_id(callback_data.user_id)

    if isinstance(query.message, Message):
        if user:
            try:
                # await repo.users.add_user(
                #     user_from_db.user_id, user.user_id
                # )
                text = as_section(
                    AdminHandlerMessages.SUCCESSFUL_UPDATING.value,
                    as_marked_list(
                        as_key_value("Пользователь", user.logged_as),
                        as_line("@", user.username),
                    ),
                )
                logger.debug(f"Choosen user: {text.as_kwargs()}")

                answer = await query.message.answer(
                    text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                logger.error(
                    f"Error updating users:\n {str(e)} \n{(await state.get_state())}"
                )
                answer = await query.message.answer(
                    "\n".join([AdminHandlerMessages.UNSUCCESSFUL_UPDATING, str(e)])
                )
            await query.message.delete()

        else:
            answer = await query.message.edit_text("User not found!")

        await state.clear()
        await state.update_data(
            prev_bot_message=answer,
        )

    logger.debug(f"{await state.get_state()}, {await state.get_data()}")

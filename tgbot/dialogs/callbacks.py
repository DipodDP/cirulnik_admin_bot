from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_key_value, as_marked_list, as_section
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from betterlogging import logging

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.dialogs.states import ActionSelectionStates, UsersMenuStates
from tgbot.keyboards.reply import admin_menu_keyboard
from tgbot.messages.handlers_msg import DatabaseHandlerMessages, UserHandlerMessages

logger = logging.getLogger(__name__)


async def set_prev_message(
    callback_query: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    if not isinstance(callback_query.message, Message):
        return
    data = dialog_manager.middleware_data
    state: FSMContext = data["state"]
    await callback_query.message.delete()
    answer = await callback_query.message.answer(
        UserHandlerMessages.CANCEL, reply_markup=admin_menu_keyboard()
    )
    await state.update_data(prev_bot_message=answer)
    await dialog_manager.done()


async def selected_user(
    callback_query: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data["user_id"] = int(item_id)
    # event = dialog_manager.event
    # middleware_data = dialog_manager.middleware_data
    # start_data = dialog_manager.start_data
    logger.debug(f"Dialog data: {dialog_manager.dialog_data}")
    await dialog_manager.switch_to(UsersMenuStates.users_actions)
    # or
    # await dialog_manager.next()


async def user_deletion(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    middleware_data = dialog_manager.middleware_data
    repo: RequestsRepo | None = middleware_data.get("repo")
    user_id: int | None = dialog_manager.dialog_data.get("user_id")

    logger.info(f"Deleting user {user_id}")

    if not user_id or repo is None:
        await dialog_manager.done()
        return

    if isinstance(callback_query.message, Message) and user_id:
        try:
            user = await repo.users.del_user_by_id(user_id)
            text = as_section(
                DatabaseHandlerMessages.SUCCESSFUL_UPDATING.value,
                as_marked_list(
                    as_key_value("Удален", "@" + user.username),
                ),
            )
            logger.debug(f"Deleted user: {text.as_kwargs()}")
            text = text.as_markdown()
        except Exception as e:
            logger.error(f"Error updating user:\n {str(e)}")
            text = DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING
    else:
        text = "User not found\!"

    dialog_manager.dialog_data["result_text"] = text

    logger.debug(f"Dialog data: {dialog_manager.dialog_data}")
    await dialog_manager.start(
        ActionSelectionStates.done, data=dialog_manager.dialog_data
    )


async def access_deletion(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    logger.debug(f"Dialog data: {dialog_manager.dialog_data}")
    await dialog_manager.start(
        ActionSelectionStates.location_selection, data=dialog_manager.dialog_data
    )


async def selected_location(
    callback_query: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
    # repo: RequestsRepo,
):
    middleware_data = dialog_manager.middleware_data
    repo: RequestsRepo | None = middleware_data.get("repo")
    user_id = dialog_manager.start_data.get("user_id")
    location_id = int(item_id)

    logger.info(f"Deleting from user {user_id}, location {location_id}")

    if not user_id or not location_id or not repo:
        await dialog_manager.done()
        return

    location = await repo.locations.get_location_by_id(location_id)
    if isinstance(callback_query.message, Message) and all([user_id, location_id]):
        if location:
            try:
                await repo.users.del_user_location(user_id, location_id)
                text = as_section(
                    DatabaseHandlerMessages.SUCCESSFUL_UPDATING.value,
                    as_marked_list(
                        as_key_value("Филиал", location.location_name),
                        as_key_value("Адрес", location.address),
                    ),
                )
                logger.debug(f"Choosen location: {text.as_kwargs()}")
                text = text.as_markdown()
            except Exception as e:
                logger.error(f"Error updating locations:\n {str(e)}")
                text = DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING
        else:
            text = "Location not found\!"

        dialog_manager.dialog_data["result_text"] = text
        await dialog_manager.switch_to(ActionSelectionStates.done)


async def action_done(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    if not isinstance(callback_query.message, Message):
        return
    data = dialog_manager.middleware_data
    state: FSMContext = data["state"]
    await callback_query.message.delete()
    answer = await callback_query.message.answer(
        UserHandlerMessages.COMPLETED, reply_markup=admin_menu_keyboard()
    )
    await state.update_data(prev_bot_message=answer)
    await dialog_manager.done()

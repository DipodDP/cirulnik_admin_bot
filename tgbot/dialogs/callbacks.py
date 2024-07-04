from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_key_value, as_marked_list, as_section
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from betterlogging import logging

from infrastructure.database.repo.requests import RequestsRepo
from tgbot.dialogs.states import ActionSelectionStates
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

    await dialog_manager.switch_to(ActionSelectionStates.location_selection)
    # or
    # await dialog_manager.next()


async def selected_location(
    callback_query: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
    # repo: RequestsRepo,
):
    # dialog_manager.dialog_data["location_id"] = item_id
    middleware_data = dialog_manager.middleware_data
    repo: RequestsRepo | None = middleware_data.get("repo")
    user_id = dialog_manager.dialog_data.get("user_id")
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
                await callback_query.message.edit_text(
                    text.as_markdown(), parse_mode=ParseMode.MARKDOWN_V2
                )
            except Exception as e:
                logger.error(f"Error updating locations:\n {str(e)}")
                await callback_query.message.edit_text(
                    "\n".join([DatabaseHandlerMessages.UNSUCCESSFUL_UPDATING, str(e)])
                )
        else:
            await callback_query.message.edit_text("Location not found!")

        # await dialog_manager.done()
    await dialog_manager.switch_to(ActionSelectionStates.done)


async def done_adding_location(
    callback_query: CallbackQuery,
    widget: Button,
    dialog_manager: DialogManager,
):
    await dialog_manager.done()

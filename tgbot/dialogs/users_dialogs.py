from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    ScrollingGroup,
    Select,
)
from aiogram_dialog.widgets.text import Const, Format

from tgbot.dialogs.callbacks import (
    access_deletion,
    action_done,
    selected_location,
    selected_user,
    set_prev_message,
)
from tgbot.dialogs.getters import get_selected_user, get_user_locations, get_users
from tgbot.dialogs.states import (
    ActionSelectionStates,
    UsersMenuStates,
)
from tgbot.keyboards.reply import NavButtons
from tgbot.messages.dialogs_msg import UsersDialogsMessages


async def close_dialog(_, __, dialog_manager: DialogManager, **kwargs):
    await dialog_manager.done()


users_menu_dialog = Dialog(
    Window(
        Const(UsersDialogsMessages.CHOOSE_USER),
        ScrollingGroup(
            Select(
                id="users_select",
                items="users", item_id_getter=lambda item: item["user_id"],
                on_click=selected_user,
                text=Format("💇🏼‍♀️ {item[name]}"),
            ),
            id="users_group",
            height=6,
            width=1,
            hide_on_single_page=True,
        ),
        Cancel(Const(NavButtons.BTN_BACK), on_click=set_prev_message),
        getter=get_users,
        state=UsersMenuStates.user_selection,
    ),
    Window(
        Const(UsersDialogsMessages.CHOOSE_ACTION),
        Column(
            Button(
                Const(UsersDialogsMessages.USER_DELETING),
                id="user_deleting",
                on_click=access_deletion
            ),
            Button(
                Const(UsersDialogsMessages.ACCESS_DELETING),
                id="access_deleting",
                on_click=access_deletion
            ),
        ),
        Cancel(Const(NavButtons.BTN_CANCEL), on_click=set_prev_message),
        getter=get_selected_user,
        state=UsersMenuStates.users_actions,
    ),
    on_process_result=close_dialog,
)

accsess_deletion_dialog = Dialog(
    Window(
        Const(UsersDialogsMessages.CHOOSE_LOCATION),
        ScrollingGroup(
            Select(
                id="locations_select",
                items="locations",
                item_id_getter=lambda item: item.location_id,
                text=Format("✂️ {item.location_name}"),
                on_click=selected_location,
            ),
            id="time_group",
            height=4,
            width=2,
            hide_on_single_page=True,
        ),
        Cancel(Const(NavButtons.BTN_CANCEL), on_click=set_prev_message),
        state=ActionSelectionStates.location_selection,
        getter=get_user_locations,
    ),
    Window(
        Format("{dialog_data[result_text]}"),
        Button(Const(NavButtons.BTN_OK), id="done", on_click=action_done),
        state=ActionSelectionStates.done,
        parse_mode=ParseMode.MARKDOWN_V2,
    ),
    on_process_result=close_dialog,
)

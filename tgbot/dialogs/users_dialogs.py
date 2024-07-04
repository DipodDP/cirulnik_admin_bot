from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Column,
    ScrollingGroup,
    Select,
    Start,
)
from aiogram_dialog.widgets.text import Const, Format

from tgbot.dialogs.callbacks import (
    done_adding_location,
    selected_location,
    selected_user,
    set_prev_message,
)
from tgbot.dialogs.getters import get_user_locations, get_users
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
        Const(UsersDialogsMessages.CHOOSE_ACTION),
        Column(
            Start(
                Const(UsersDialogsMessages.USER_DELETING),
                id="user_deleting",
                state=ActionSelectionStates.access_deleting,
            ),
            Start(
                Const(UsersDialogsMessages.ACCESS_DELETING),
                id="access_deleting",
                state=ActionSelectionStates.access_deleting,
            ),
            Cancel(Const(NavButtons.BTN_BACK), on_click=set_prev_message),
        ),
        state=UsersMenuStates.users,
    ),
)


user_selection_dialog = Dialog(
    Window(
        Const(UsersDialogsMessages.CHOOSE_USER),
        ScrollingGroup(
            Select(
                id="users_select",
                items="users",
                item_id_getter=lambda item: item["user_id"],
                on_click=selected_user,
                text=Format("💇🏼‍♀️ {item[name]}"),
            ),
            id="users_group",
            height=6,
            width=1,
            hide_on_single_page=True,
        ),
        Cancel(Const(NavButtons.BTN_CANCEL)),
        getter=get_users,
        state=ActionSelectionStates.access_deleting,
    ),
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
        Back(Const(NavButtons.BTN_BACK)),
        Cancel(Const(NavButtons.BTN_CANCEL)),
        state=ActionSelectionStates.location_selection,
        getter=get_user_locations,
    ),
    Window(
        Const(UsersDialogsMessages.CONTINUE),
        Button(Const(NavButtons.BTN_OK), id="done", on_click=done_adding_location),
        state=ActionSelectionStates.done,
    ),
    on_process_result=close_dialog,
)

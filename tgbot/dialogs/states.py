from aiogram.fsm.state import State, StatesGroup


class UsersMenuStates(StatesGroup):
    users_actions = State()
    user_selection = State()


class ActionSelectionStates(StatesGroup):
    user_deleting = State()
    access_deleting = State()
    location_selection = State()
    done = State()

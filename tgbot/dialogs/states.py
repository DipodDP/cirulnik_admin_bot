from aiogram.fsm.state import State, StatesGroup


class UsersMenuStates(StatesGroup):
    users = State()


class ActionSelectionStates(StatesGroup):
    # selection = State()
    user_deleting = State()
    access_deleting = State()
    location_selection = State()
    done = State()

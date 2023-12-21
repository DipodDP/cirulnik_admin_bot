from aiogram.fsm.state import State, StatesGroup


class ReportMenuStates(StatesGroup):
    creating_report = State()
    choosing_location = State()
    entering_masters_quantity = State()
    entering_latecomers = State()
    entering_absent = State()
    completing_report = State()

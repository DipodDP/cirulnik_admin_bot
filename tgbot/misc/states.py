from aiogram.fsm.state import State, StatesGroup


class ReportMenuStates(StatesGroup):
    creating_report = State()
    choosing_location = State()

    # Morning report
    entering_masters_quantity = State()
    entering_latecomers = State()
    entering_absent = State()
    uploading_open_check = State()

    # Evening report
    entering_clients_lost = State()
    entering_total_clients = State()
    uploading_daily_excel = State()
    uploading_z_report = State()
    entering_sbp_sum = State()
    entering_day_resume = State()
    entering_disgruntled_clients = State()
    entering_argues_with_masters = State()

    completing_report = State()

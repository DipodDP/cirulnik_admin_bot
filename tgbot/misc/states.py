from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class CommonStates(StatesGroup):
    unauthorized = State()
    authorized = State()

    async def check_auth(self, state: FSMContext) -> bool:
        """
        Check if there is 'author' in state and sets 'authorized' state if so.
        Return True if authorized.
        :param state: state from FSM.
        :type state: FSMContext
        :return: bool
        """
        state_data = await state.get_data()
        if all(
            [
                state_data.get("author") is not None,
                state_data.get("author_name") is not None,
            ]
        ):
            await state.set_state(self.authorized)
            return True
        else:
            await state.set_state(self.unauthorized)
            return False


class AdminStates(StatesGroup):
    updating_locations = State()
    updating_user_location = State()


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

    # Common states
    uploading_solarium_counter = State()
    completing_report = State()

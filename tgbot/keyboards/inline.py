from collections.abc import Sequence
from enum import Enum

from aiogram.filters.callback_data import CallbackData

# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.database.models.locations import Location
from infrastructure.database.models.users import User


class InlineButtons(str, Enum):
    MORNING = "☀️ Утро"
    EVENING = "🌙 Вечер"


# This is a simple keyboard, that contains 2 buttons
# def very_simple_keyboard():
#     buttons = [
#         [
#             InlineKeyboardButton(text="📝 Create an location",
#                                  callback_data="create_location"),
#             InlineKeyboardButton(text="📋 My locations",
#                                  callback_data="my_locations"),
#         ],
#     ]
#
#     keyboard = InlineKeyboardMarkup(
#         inline_keyboard=buttons,
#     )
#     return keyboard


# This is the same keyboard, but created with InlineKeyboardBuilder (preferred way)
def daytime_keyboard():
    # First, you should create an InlineKeyboardBuilder object
    keyboard = InlineKeyboardBuilder()

    # You can use keyboard.button() method to add buttons, then enter text and callback_data
    keyboard.button(text=InlineButtons.MORNING, callback_data="morning")
    keyboard.button(
        text=InlineButtons.EVENING,
        # In this simple example, we use a string as callback_data
        callback_data="evening",
    )

    # If needed you can use keyboard.adjust() method to change the number of buttons per row
    # keyboard.adjust(2)

    # Then you should always call keyboard.as_markup() method to get a valid InlineKeyboardMarkup object

    return keyboard.as_markup()


# For a more advanced usage of callback_data, you can use the CallbackData factory
class UserCallbackData(CallbackData, prefix="user"):
    """
    This class represents a CallbackData object for users.

    - When used in InlineKeyboardMarkup, you have to create an instance of this class, run .pack() method, and pass to callback_data parameter.

    - When used in InlineKeyboardBuilder, you have to create an instance of this class and pass to callback_data parameter (without .pack() method).

    - In handlers you have to import this class and use it as a filter for callback query handlers, and then unpack callback_data parameter to get the data.
    """

    user_id: int | None
    location_id: int | None


def users_update_keyboard(
    users: Sequence[User],
    location_id: int | None = None,
):
    # Here we use a list of users as a parameter (from simple_menu.py)

    keyboard = InlineKeyboardBuilder()
    for user in users:
        keyboard.button(
            text=f"💇🏼‍♀️ {user.logged_as if user.logged_as else user.full_name}",
            # Here we use an instance of UserCallbackData class as callback_data parameter
            # user id is the field in UserCallbackData class, that we defined above
            callback_data=UserCallbackData(
                user_id=user.user_id, location_id=location_id
            ),
        )

    keyboard.adjust(1)

    return keyboard.as_markup()


def locations_keyboard(
    locations: Sequence[Location],
    user_id: int | None = None,
):
    keyboard = InlineKeyboardBuilder()
    for location in locations:
        keyboard.button(
            text=f"✂️ {location.location_name}",
            callback_data=UserCallbackData(
                user_id=user_id, location_id=location.location_id
            ),
        )

    keyboard.adjust(1)

    return keyboard.as_markup()

"""Import all routers and add them to routers_list."""

from .admin import admin_router
from .auth import auth_router
from .database_users import database_users_router
from .database_locations import database_locations_router
from .report_menu import report_menu_router
from .report_morning import report_morning_router
from .report_evening import report_evening_router
from .report_nav_buttons import report_nav_buttons_router
from .user import user_router
from .echo import echo_router

routers_list = [
    admin_router,
    auth_router,
    database_users_router,
    database_locations_router,
    user_router,
    report_nav_buttons_router,
    report_menu_router,
    report_morning_router,
    report_evening_router,
    echo_router,  # echo_router must be last
]

__all__ = [
    "routers_list",
]

"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .echo import echo_router
from .report_menu import report_menu_router
from .report_morning import report_morning_router
from .report_nav_buttons import report_nav_buttons_router
from .user import user_router

routers_list = [
    admin_router,
    report_menu_router,
    user_router,
    report_nav_buttons_router,
    report_morning_router,
    echo_router,  # echo_router must be last
]

__all__ = [
    "routers_list",
]

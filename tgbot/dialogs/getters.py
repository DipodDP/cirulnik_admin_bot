from aiogram_dialog import DialogManager

from infrastructure.database.repo.requests import RequestsRepo


async def get_users(dialog_manager: DialogManager, repo: RequestsRepo, **kwargs):
    users = await repo.users.get_all_users()
    items = [
        {
            "user_id": user.user_id,
            "name": f"{user.logged_as if user.logged_as else user.full_name}",
        }
        for user in users
    ]

    return {"users": (items)}

async def get_selected_user(dialog_manager: DialogManager, repo: RequestsRepo, **kwargs):

    user_id = dialog_manager.dialog_data["user_id"]
    return {"user_id": user_id}

async def get_user_locations(
    dialog_manager: DialogManager, repo: RequestsRepo, **kwargs
):
    user_id = dialog_manager.start_data["user_id"]
    locations = await repo.users.get_all_user_locations_relationships(user_id)

    return {"locations": (locations)}

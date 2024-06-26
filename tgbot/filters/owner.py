from aiogram.filters import BaseFilter
from aiogram.types import Message

from infrastructure.database.repo.requests import RequestsRepo


class OwnerFilter(BaseFilter):
    is_owner: bool = True

    async def __call__(self, obj: Message, repo: RequestsRepo) -> bool:
        is_owner = (
            await repo.users.get_user_is_owner(
                obj.from_user.id,
            )
            if obj.from_user is not None
            else False
        )

        return is_owner == self.is_owner

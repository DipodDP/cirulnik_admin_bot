from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from infrastructure.database.repo.requests import RequestsRepo


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, session_pool) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message | CallbackQuery):
            print(
                "{} used not for Message, but for {}".format(
                    self.__class__.__name__, type(event).__name__
                ),
            )
            return await handler(event, data)

        async with self.session_pool() as session:
            repo = RequestsRepo(session)
            event_from_user = data.get("event_from_user")

            user = (
                await repo.users.get_or_upsert_user(
                    event_from_user.id,
                    event_from_user.username,
                    event_from_user.full_name,
                    event_from_user.language_code,
                )
                if event_from_user is not None
                else None
            )

            # access to session in handlers: repo.session.execute(stmt)
            data["repo"] = repo
            data["user_from_db"] = user

            result = await handler(event, data)
        return result

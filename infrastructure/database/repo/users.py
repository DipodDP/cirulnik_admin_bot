from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.mysql import insert as my_insert

from infrastructure.database.models import User
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_create_user(
        self,
        user_id: int,
        full_name: str,
        language: str | None,
        username: Optional[str] = None,
    ):
        """
        Creates or updates a new user in the database and returns the user object.
        :param user_id: The user's ID.
        :param full_name: The user's full name.
        :param language: The user's language.
        :param username: The user's username. It's an optional parameter.
        :return: User object, None if there was an error while making a transaction.
        """
        try:
            insert_stmt = (
                pg_insert(User)
                .values(
                    user_id=user_id,
                    username=username,
                    full_name=full_name,
                    language=language,
                )
                .on_conflict_do_update(
                    index_elements=[User.user_id],
                    set_=dict(
                        username=username,
                        full_name=full_name,
                    ),
                )
                .returning(User)
            )
        except AttributeError:
            insert_stmt = (
                my_insert(User)
                .values(
                    user_id=user_id,
                    username=username,
                    full_name=full_name,
                    language=language,
                )
                .on_duplicate_key_update(
                    username=username,
                    full_name=full_name,
                )
            )

        result = await self.session.execute(insert_stmt)

        await self.session.commit()
        return result.scalar_one()

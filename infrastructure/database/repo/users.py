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
        full_name: Optional[str] = None,
        language: Optional[str] = None,
        username: Optional[str] = None,
        logged_as: Optional[str] = None,
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
                    # logged_as=logged_as,
                )
                .on_conflict_do_update(
                    index_elements=[User.user_id],
                    set_=dict(
                        username=username, full_name=full_name, language=language
                    ),
                )
                .returning(User)
            )

            result = await self.session.execute(insert_stmt)

        except Exception as e:
            print(e)
            insert_stmt = (
                my_insert(User)
                .values(
                    user_id=user_id,
                    username=username,
                    full_name=full_name,
                    language=language,
                    # logged_as=logged_as,
                )
                .on_duplicate_key_update(
                    username=username, full_name=full_name, language=language
                )
            )

            await self.session.execute(insert_stmt)
            # Flush the session to ensure the insert/update operation is executed
            await self.session.flush()
            # Query the user after insertion/updation
            user_query = select(User).where(User.user_id == user_id)
            result = await self.session.execute(user_query)

        await self.session.commit()
        scalar = result.scalar_one()

        return scalar

    async def get_user_by_id(self, telegram_id: int):
        select_stmt = select(User).where(User.user_id == telegram_id)
        result = await self.session.execute(select_stmt)

        return result.scalars().first()

    async def get_all_users(self):
        select_stmt = select(User).order_by(User.username.asc()).having(User.active)
        result = await self.session.execute(select_stmt)

        return result.scalars().all()

    async def get_user_logged_as(self, telegram_id: int):
        select_stmt = select(User.logged_as).where(User.user_id == telegram_id)
        result = await self.session.execute(select_stmt)

        return result.scalar()

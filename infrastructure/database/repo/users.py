from collections.abc import Sequence
from typing import Optional
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.mysql import insert as my_insert

from infrastructure.database.models import User
from infrastructure.database.models.locations import Location, UserLocation
from infrastructure.database.repo.base import BaseRepo


class UserRepo(BaseRepo):
    async def get_or_upsert_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        full_name: Optional[str] = None,
        language: str = "en",
        # logged_as: Optional[str] = None,
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

    async def set_user_logged_as(self, telegram_id: int, logged_as: str | None):
        insert_stmt = (
            update(User).where(User.user_id == telegram_id).values(logged_as=logged_as)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()

        return result.last_updated_params()

    async def get_user_by_id(self, telegram_id: int):
        select_stmt = select(User).where(User.user_id == telegram_id)
        result = await self.session.execute(select_stmt)

        return result.scalars().first()

    async def get_all_users(self):
        select_stmt = (
            select(User)
            .where(User.active)
            # .join(UserLocation, User.user_id == UserLocation.user_id)
            # .join(Location, UserLocation.location_id == Location.location_id)
            .order_by(User.username.asc())
        )
        result = await self.session.execute(select_stmt)

        return result.scalars().all()

    async def get_user_logged_as(self, user_id: int):
        select_stmt = select(User.logged_as).where(User.user_id == user_id)
        result = await self.session.execute(select_stmt)

        return result.scalar()

    async def get_all_user_locations_relationships(self, user_id: int):
        stmt = (
            select(Location, User.username)
            .join(User.locations)
            .join(Location)
            .where(User.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add_user_location(self, user_id: int, location_id: int):
        insert_stmt = insert(UserLocation).values(
            user_id=user_id, location_id=location_id
        )
        await self.session.execute(insert_stmt)
        await self.session.commit()

    async def del_user_location(self, user_id: int, location_id: int):
        insert_stmt = delete(UserLocation).where(
            UserLocation.user_id == user_id, UserLocation.location_id == location_id
        )
        await self.session.execute(insert_stmt)
        await self.session.commit()

    async def get_all_users_locations(self) -> Sequence[UserLocation]:
        """
        Retrieve all user locations, ordered by user_id.
        :return: List of UserLocation objects.
        """

        select_stmt = select(UserLocation).order_by(UserLocation.user_id.asc())
        result = await self.session.execute(select_stmt)

        return result.scalars().all()

    async def get_all_locations_by_user(self, user_id: int) -> Sequence[UserLocation]:
        """
        Retrieve all locations for a specific user, ordered by location_id.
        :return: List of UserLocation objects.
        """

        select_stmt = (
            select(UserLocation)
            .where(UserLocation.user_id == user_id)
            .order_by(UserLocation.location_id.asc())
        )
        result = await self.session.execute(select_stmt)

        return result.scalars().all()

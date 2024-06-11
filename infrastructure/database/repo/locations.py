from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.mysql import insert as my_insert

from infrastructure.database.models import Location
from infrastructure.database.repo.base import BaseRepo


class LocationRepo(BaseRepo):
    async def get_or_create_location(
        self,
        location_id: int,
        locationname: Optional[str] = None,
        full_name: Optional[str] = None,
        language: str = 'en',
        # logged_as: Optional[str] = None,
    ):
        """
        Creates or updates a new location in the database and returns the location object.
        :param location_id: The location's ID.
        :param full_name: The location's full name.
        :param language: The location's language.
        :param locationname: The location's locationname. It's an optional parameter.
        :return: Location object, None if there was an error while making a transaction.
        """
        try:
            insert_stmt = (
                pg_insert(Location)
                .values(
                    location_id=location_id,
                    locationname=locationname,
                    full_name=full_name,
                    language=language,
                    # logged_as=logged_as,
                )
                .on_conflict_do_update(
                    index_elements=[Location.location_id],
                    set_=dict(
                        locationname=locationname, full_name=full_name, language=language
                    ),
                )
                .returning(Location)
            )

            result = await self.session.execute(insert_stmt)

        except Exception as e:
            print(e)
            insert_stmt = (
                my_insert(Location)
                .values(
                    location_id=location_id,
                    locationname=locationname,
                    full_name=full_name,
                    language=language,
                    # logged_as=logged_as,
                )
                .on_duplicate_key_update(
                    locationname=locationname, full_name=full_name, language=language
                )
            )

            await self.session.execute(insert_stmt)
            # Flush the session to ensure the insert/update operation is executed
            await self.session.flush()
            # Query the location after insertion/updation
            location_query = select(Location).where(Location.location_id == location_id)
            result = await self.session.execute(location_query)

        await self.session.commit()
        scalar = result.scalar_one()

        return scalar

    async def set_location_logged_as(self, telegram_id: int, logged_as: str | None):
        insert_stmt = update(Location).where(Location.location_id == telegram_id).values(logged_as = logged_as)
        result = await self.session.execute(insert_stmt)
        await self.session.commit()

        return result.last_updated_params()

    async def get_location_by_id(self, telegram_id: int):
        select_stmt = select(Location).where(Location.location_id == telegram_id)
        result = await self.session.execute(select_stmt)

        return result.scalars().first()

    async def get_all_locations(self):
        select_stmt = select(Location).order_by(Location.location_name.asc())
        result = await self.session.execute(select_stmt)

        return result.scalars().all()

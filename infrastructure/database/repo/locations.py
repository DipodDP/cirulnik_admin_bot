from typing import Optional
from sqlalchemy import select, text, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.mysql import insert as my_insert

from infrastructure.database.models import Location
from infrastructure.database.repo.base import BaseRepo


class LocationRepo(BaseRepo):
    async def get_or_upsert_location(
        self,
        location_name: str,
        address: str,
        location_id: Optional[int] = None,
        has_solarium: bool = False,
        # logged_as: Optional[str] = None,
    ):
        """
        Creates or updates a new location in the database and returns the location object.
        :param location_id: The location's ID.
        :param location_name: The location's location_name.
        :param address: The location's address.
        :param has_solarium: If location has solarium.
        :return: Location object, None if there was an error while making a transaction.
        """

        # Determine the dialect name
        dialect_name = self.session.bind.dialect.name

        # Common values to insert
        values = {
            "location_name": location_name,
            "address": address,
            "has_solarium": has_solarium,
        }

        if location_id:
            values["location_id"] = location_id
            index_elements = [Location.location_id]
        else:
            index_elements = [Location.location_name]

        if dialect_name == "postgresql":
            # PostgreSQL upsert statement
            insert_stmt = (
                pg_insert(Location)
                .values(**values)
                .on_conflict_do_update(index_elements=index_elements, set_=values)
                .returning(Location)
            )

            result = await self.session.execute(insert_stmt)
            inserted_location = result.scalar_one()

        elif dialect_name == "mysql":
            # MySQL upsert statement
            insert_stmt = (
                my_insert(Location).values(**values).on_duplicate_key_update(**values)
            )

            await self.session.execute(insert_stmt)
            # Flush the self.session to ensure the insert/update operation is executed
            await self.session.flush()

            # Retrieve the last inserted ID using a raw SQL query
            last_insert_id_query = text("SELECT LAST_INSERT_ID()")
            result = await self.session.execute(last_insert_id_query)
            last_id = result.scalar_one()

            if not last_id:
                location_query = select(Location).where(
                    Location.location_name == values["location_name"]
                )

            else:
                # Query the location after insertion/updation
                location_query = select(Location).where(Location.location_id == last_id)

            result = await self.session.execute(location_query)
            inserted_location = result.scalar_one()

        else:
            raise ValueError(f"Unsupported database dialect: {dialect_name}")

        await self.session.commit()
        return inserted_location

    async def set_location_logged_as(self, telegram_id: int, logged_as: str | None):
        insert_stmt = (
            update(Location)
            .where(Location.location_id == telegram_id)
            .values(logged_as=logged_as)
        )
        result = await self.session.execute(insert_stmt)
        await self.session.commit()

        return result.last_updated_params()

    async def get_location_by_id(self, location_id: int):
        select_stmt = select(Location).where(Location.location_id == location_id)
        result = await self.session.execute(select_stmt)

        return result.scalars().first()

    async def get_all_locations(self):
        select_stmt = select(Location).order_by(Location.location_name.asc())
        result = await self.session.execute(select_stmt)

        return result.scalars().all()

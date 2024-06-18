from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from faker import Faker

from infrastructure.database.repo.locations import LocationRepo
from infrastructure.database.repo.users import UserRepo


@dataclass
class RequestsRepo:
    """
    Repository for handling database operations. This class holds all the repositories for the database models.

    You can add more repositories as properties to this class, so they will be easily accessible.
    """

    session: AsyncSession

    @property
    def users(self) -> UserRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return UserRepo(self.session)

    @property
    def locations(self) -> LocationRepo:
        """
        The User repository sessions are required to manage user operations.
        """
        return LocationRepo(self.session)


if __name__ == "__main__":
    import asyncio
    import random

    from infrastructure.database.models import *
    from tgbot.config import load_config
    from infrastructure.database.setup import create_engine
    from infrastructure.database.setup import create_session_pool
    # from infrastructure.database.models.base import Base

    config = load_config(".env")
    engine = create_engine(config.db, echo=False)
    session_pool = create_session_pool(engine)

    async def example_usage():
        """
        Example usage function for the RequestsRepo class.
        Use this function as a guide to understand how to utilize RequestsRepo for managing user data.
        Pass the config object to this function for initializing the database resources.
        :param config: The config object loaded from your configuration.
        """

        async with session_pool() as session:
            repo = RequestsRepo(session)
            # Base.metadata.drop_all(engine)
            # async with engine.begin() as conn:
            #     # Use run_sync to execute the CreateTable operation
            #     await conn.run_sync(Base.metadata.drop_all)
            # async with engine.begin() as conn:
            #     # Use run_sync to execute the CreateTable operation
            #     await conn.run_sync(Base.metadata.create_all)

            # Replace user details with the actual values
            user = await repo.users.get_or_upsert_user(
                user_id=12356,
                full_name="John Doe",
                language="en",
                username="johndoe",
                # logged_as="Noname"
            )

            users = await repo.users.get_all_users()

            # Get users with their locations
            for user in users:
                print(f"User: {user.full_name} {user.username}({user.user_id})")

                user_locations = await repo.users.get_all_user_locations_relationships(
                    user_id=user.user_id
                )

                for location in user_locations:
                    print(f"# Location: {location.location_name}")

        return user

    async def seed_fake_data():
        async with session_pool() as session:
            repo = RequestsRepo(session)
        Faker.seed(42)
        fake = Faker()
        users = []
        locations = []

        for id in range(5):
            try:
                user = await repo.users.get_or_upsert_user(
                    user_id=fake.pyint(),
                    username=fake.user_name(),
                    full_name=fake.name(),
                    language=fake.language_code(),
                )
                users.append(user)
                location = await repo.locations.get_or_upsert_location(
                    location_id=id,
                    location_name=fake.street_name(),
                    address=fake.street_address(),
                    has_solarium=fake.boolean(chance_of_getting_true=65),
                )
                locations.append(location)

            except IntegrityError as e:
                await session.rollback()
                print(
                    "----------- DB exception: -----------\n",
                    e.orig,
                    "\n",
                    e.statement,
                    e.params,
                )

        try:
            for location in random.sample(locations, len(locations)):
                await repo.users.add_user_location(
                    user_id=random.choice(users).user_id,
                    location_id=location.location_id,
                )

            locations = await repo.users.get_all_users_locations()

            for location in random.sample(locations, len(locations)):
                try:
                    await repo.users.del_user_location(
                        user_id=location.user_id,
                        location_id=location.location_id,
                    )

                except IntegrityError as e:
                    print(
                        "----------- DB exception: -----------\n",
                        e.orig,
                        "\n",
                        e.statement,
                        e.params,
                    )

        except IntegrityError as e:
            await session.rollback()
            print(
                "----------- DB exception: -----------\n",
                e.orig,
                "\n",
                e.statement,
                e.params,
            )

        finally:
            await repo.session.close()

    async def main():
        await example_usage()
        await seed_fake_data()

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        ...

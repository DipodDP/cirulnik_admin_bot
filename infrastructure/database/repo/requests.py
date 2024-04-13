from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.repo.users import UserRepo
from infrastructure.database.setup import create_engine
from tgbot.config import load_config


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


if __name__ == "__main__":
    import asyncio

    from infrastructure.database.setup import create_session_pool
    from tgbot.config import Config
    
    from infrastructure.database.models import * 

    async def example_usage(config: Config):
        """
        Example usage function for the RequestsRepo class.
        Use this function as a guide to understand how to utilize RequestsRepo for managing user data.
        Pass the config object to this function for initializing the database resources.
        :param config: The config object loaded from your configuration.
        """
        engine = create_engine(config.db, echo=True)
        session_pool = create_session_pool(engine)

        async with session_pool() as session:
            repo = RequestsRepo(session)
            # Base.metadata.drop_all(engine)
            async with engine.begin() as conn:
                # Use run_sync to execute the CreateTable operation
                await conn.run_sync(Base.metadata.drop_all)
            async with engine.begin() as conn:
                # Use run_sync to execute the CreateTable operation
                await conn.run_sync(Base.metadata.create_all)

            # Replace user details with the actual values
            user = await repo.users.get_or_create_user(
                user_id=12356,
                full_name="John Doe",
                language="en",
                username="johndoe",
            )

    config = load_config(".env")
    try:
        asyncio.run(example_usage(config))
        # asyncio.gather(main(), return_exceptions=True).cancel()
    except (KeyboardInterrupt, SystemExit):
        ...

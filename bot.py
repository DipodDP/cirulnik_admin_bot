import asyncio
import logging
from aiogram.client.session.aiohttp import AiohttpSession
import betterlogging as bl
from aiogram import Bot, Dispatcher, session
from aiogram.fsm.storage.memory import MemoryStorage
from tgbot.middlewares.albums_collector import AlbumsMiddleware
from tgbot.misc.notify_admins import on_down, on_startup
from tgbot.misc.setting_comands import set_all_default_commands
# from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder

from tgbot.config import load_config, Config
from tgbot.handlers import routers_list
from tgbot.middlewares.config import ConfigMiddleware

# from infrastructure.database.repo.requests import engine, session_pool 
# from infrastructure.database.models import * 


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        AlbumsMiddleware(2),
        # DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging(log_level: str):
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    # bl.basic_colorized_config(level=log_level)
    logging.basicConfig(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        # return RedisStorage.from_url(
        #     config.redis.dsn(),
        #     key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        # )
        ...
    else:
        return MemoryStorage()


async def main():
    config = load_config(".env")

    setup_logging(config.tg_bot.console_log_level)
    logger = logging.getLogger(__name__)
    logger.debug(config)

    storage = get_storage(config)

    # Proxy URL with credentials:
    # "protocol://user:password@host:port"
    session = AiohttpSession(config.tg_bot.proxy_url) if config.tg_bot.proxy_url else None
    bot = Bot(token=config.tg_bot.token, parse_mode="HTML", session=session)
    dp = Dispatcher(storage=storage)

    dp.include_routers(*routers_list)

    register_global_middlewares(dp, config)
    await set_all_default_commands(bot)

    try:
        await on_startup(bot, config.tg_bot.admin_ids)
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)

    except Exception as e:
        logging.exception(e)
        # await dp.stop_polling()
        ...
    finally:
        await on_down(bot, config.tg_bot.admin_ids)
        await bot.session.close()
        await dp.emit_shutdown()
        await dp.storage.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
        # asyncio.gather(main(), return_exceptions=True).cancel()
    except (KeyboardInterrupt, SystemExit):
        logging.warning("Bot is stopped!")

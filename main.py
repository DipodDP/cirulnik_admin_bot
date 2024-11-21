import asyncio
import sys

from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    setup_application,
)
from aiohttp.web_app import Application
from tgbot.core.loader import logger, dp, bot, config, WEBHOOK_PATH
from aiohttp import web


def main():
    # Override webhook host url from env by url from cli
    if len(sys.argv) > 1:
        setattr(config.tg_bot, 'webhook_host', sys.argv[1])

    if url := config.tg_bot.webhook_host:
        logger.info(f"Using webhook: {url + WEBHOOK_PATH}")
        run_webhook_server()

    else:
        logger.info("Using long polling...")
        asyncio.run(run_polling())


def run_webhook_server():

    app = Application()

    SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    ).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    web.run_app(
        app, host=config.tg_bot.webapp_host, port=config.tg_bot.webapp_port
    )


async def run_polling():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logger.warning("Bot is stopped!")

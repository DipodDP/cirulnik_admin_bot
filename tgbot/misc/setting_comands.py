from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


DEF_COMMANDS = {
    'ru': [
        BotCommand(command='/start', description='Запустить бота'),
        BotCommand(command='/help', description='Помощь по боту'),
        BotCommand(command='/menu', description='Меню')
    ],
    'en': [
        BotCommand(command='/start', description='Bot start'),
        BotCommand(command='/help', description='Bot help'),
        BotCommand(command='/menu', description='Menu')
    ]
}


async def set_all_default_commands(bot: Bot):

    for language_code, commands in DEF_COMMANDS.items():
        await bot.set_my_commands(
            commands=commands,
            scope=BotCommandScopeDefault(),
            language_code=language_code
        )

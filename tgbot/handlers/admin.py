from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.reply import user_menu_keyboard
from tgbot.messages.handlers_msg import AdminHandlerMessages


admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message):
    await message.reply(AdminHandlerMessages.GREETINGS, reply_markup=user_menu_keyboard())
#     await message.reply('Troposcatter calculation', reply_markup=main_menu)


@admin_router.message(Command('stop'))
async def stop_bot(message: Message):
    await message.reply(AdminHandlerMessages.STOPPING)
    await message.delete()
    exit()

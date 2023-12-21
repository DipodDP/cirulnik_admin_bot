from enum import Enum

from aiogram.utils.markdown import hcode

from tgbot.keyboards.reply import NavButtons


sep = '\n'

class AdminHandlerMessages(str, Enum):
    GREETINGS = "Hello, admin! It's Cirulnic admin bot.\n Press /stop to stop bot\n"
    STOPPING = 'Stopping bot...'

class UserHandlerMessages(str, Enum):
    GREETINGS = "Hello! It's Cirulnic admin bot."
    HELP = "Try some commands from menu"

class ReportHandlerMessages(str, Enum):
    CHOOSE_DAYTIME = 'Выберите время суток:'
    CHOOSE_LOCATION = 'Выберите салон, в котором сегодня работаете:'
    MASTERS_QUANTITY = f"Сколько сегодня мастеров на смене? Скопируйте и укажите количество:\n{hcode('- мужской зал: ', '- женский зал: ', '- маникюр: ', '- косметолог: ', '- бровист: ', '- лэшмейкер: ', sep=sep)}{sep}    💇‍♀️ 💇"
    LATECOMERS = 'Есть ли опоздавшие? Кто?'
    ABSENT = 'Есть ли не вышедшие на работу? Кто? Причина?'
    SEND_REPORT = f'Нажмите кнопку "{NavButtons.BTN_SEND.value}" чтобы отправить отчет'
    REPORT_COMPLETED = 'Спасибо, отчет отправлен!'
    REPORT_CANCELED = 'Отправка отчета отменена!'


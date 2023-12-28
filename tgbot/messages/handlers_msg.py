from enum import Enum

from aiogram.utils.markdown import hpre

from tgbot.keyboards.reply import NavButtons, ReplyButtons


sep = '\n'

class AdminHandlerMessages(str, Enum):
    GREETINGS = "Hello, admin! It's Cirulnik admin bot.\n Press /stop to stop bot\n"
    STOPPING = 'Stopping bot...'

class UserHandlerMessages(str, Enum):
    GREETINGS = '{user}, добрый день, это бот администратора салонa "Цирюльник"' 
    ASK_USERNAME = 'Ошибка, не указано имя пользователя Telegram!\n\nПожалуйста, укажите `Имя пользователя` в настройках аккаунта Telegram для продолжения работы с ботом.'
    HELP = f'Нажмите команду /start и кнопку "{ReplyButtons.BTN_SEND_REPORT.value}"'
    AUTHORIZATION = 'Ввведите свое имя и фамилию'

class ReportHandlerMessages(str, Enum):
    CHOOSE_DAYTIME = 'Выберите время суток:'
    CHOOSE_LOCATION = 'Выберите салон, в котором сегодня работаете:'

    # Morning report messages
    MASTERS_QUANTITY = f"Сколько сегодня мастеров на смене?\nНажмите чтобы скопировать и укажите количество:\n{hpre('- мужской зал: ', '- женский зал: ', '- маникюр: ', '- косметолог: ', '- бровист: ', '- лэшмейкер: ', '', '💇*********💇‍♀️')}"
    LATECOMERS = 'Есть ли опоздавшие? Кто?'
    ABSENT = 'Есть ли не вышедшие на работу? Кто? Причина?'
    OPEN_CHECK = 'Загрузите фото чека открытия смены'

    # Evening report messages
    CLIENTS_LOST = f"Сколько клиентов было упущено сегодня?\nНажмите чтобы скопировать и укажите количество:\n{hpre('', '************', '', '- мужской зал: ', '- женский зал: ', '- маникюр: ', '', '💇*********💇‍♀️')}"
    TOTAL_CLIENTS = 'Укажите сколько всего клиентов было:'
    DAILY_EXCEL = 'Загрузите фото ежедневного Excel отчета'
    Z_REPORT = 'Загрузите фото зет отчета и сверки итогов'
    SBP_SUM = 'Введите сумму по СБП'
    DAY_RESUME = 'Расскажите как прошел день:'
    DISGRUNTLED_CLIENTS = 'Были ли недовольные клиенты?'
    ARGUES_WITH_MASTERS = 'Были ли конфликты/споры с мастерами/между мастерами?'

    SEND_REPORT = f'Нажмите кнопку "{NavButtons.BTN_SEND.value}" чтобы отправить отчет'
    REPORT_CANCELED = 'Отправка отчета отменена!'
    REPORT_MORNING_COMPLETED = 'Спасибо, утренний отчет отправлен!☀️'
    REPORT_EVENING_COMPLETED = 'Спасибо, вечерний отчет отправлен!🌙'


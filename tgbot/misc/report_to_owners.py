from typing import Any, Tuple
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Bold, HashTag, Text, as_list, as_section
from betterlogging import logging

from tgbot.services import broadcaster


logger = logging.getLogger(__name__)


class ReportBuilder():
    def __init__(self, data: dict[str, Any]):
        self.location: Text | None = data['location']
        self.author: str | None = '@' + data['author']
        self.author_name: str | None = data['author_name']
        # Morning report
        self.masters_quantity: dict[str, str] = data['masters_quantity'] if 'masters_quantity' in data else {'data': 'N/A'}
        self.latecomers: str | None = data['latecomers'] if 'latecomers' in data else None
        self.absent: str | None = data['absent'] if 'absent' in data else None
        self.location_text: Tuple[str] = self.location.as_kwargs()['text'] if self.location else (''),
        # Evening report
        self.clients_lost: dict[str, str] = data['clients_lost'] if 'clients_lost' in data else {'data': 'N/A'}
        self.total_clients: str | None = data['total_clients'] if 'total_clients' in data else None
        self.sbp_sum: str | None = data['sbp_sum'] if 'sbp_sum' in data else None
        self.day_resume: str | None = data['day_resume'] if 'day_resume' in data else None
        self.disgruntled_clients: str | None = data['disgruntled_clients'] if 'disgruntled_clients' in data else None
        self.argues_with_masters: str | None = data['argues_with_masters'] if 'argues_with_masters' in data else None

    def construct_morning_report(self) -> str:
        content = as_list(
            Bold(
                'Утренний отчет ☀️'
            ),
            HashTag(self.location_text[0].split('\n')[0].split(': ')[1].replace(' ', '_')),
            self.location.as_kwargs()['text'] if self.location else None,
            as_section(
                Bold('Администратор:'),
                f'{self.author_name} ({self.author})',
                Bold('\n\nMастеров на смене:\n'),
                '\n'.join([
                    f'{k} {v}' for k, v in self.masters_quantity.items()
                ]),
                Bold('\n\nОпоздали:\n'),
                self.latecomers,
                Bold('\n\nОтсутствуют:\n'),
                self.absent
            )
        )
        return content.as_markdown()

    def construct_evening_report(self) -> str:
        content = as_list(
            Bold(
                'Вечерний отчет 🌙'
            ),
            HashTag(self.location_text[0].split('\n')[0].split(': ')[1].replace(' ', '_')),
            self.location.as_kwargs()['text'] if self.location else None,
            as_section(
                Bold('Администратор:'),
                f'{self.author_name} ({self.author})',
                Bold('\n\nУпущено клиентов:\n'),
                '\n'.join([
                    f'{k} {v}' for k, v in self.clients_lost.items()
                ]),
                Bold('\n\nВсего клиентов:\n'),
                self.total_clients,
                Bold('\n\nСумма СБП: \n'),
                self.sbp_sum,
                Bold('\n\nКак прошел день: \n'),
                self.day_resume,
                Bold('\n\nНедовольные клиенты: \n'),
                self.disgruntled_clients,
                Bold('\n\nКонфликты/споры с мастерами/между мастерами: \n'),
                self.argues_with_masters,
            )
        )
        return content.as_markdown()

async def on_report(bot: Bot | None, admin_ids: list[int | str], report: str):

    try:
        logger.info(f"Sending report {report}...")
        await broadcaster.broadcast(
            bot,
            admin_ids,
            report,
            parse_mode=ParseMode.MARKDOWN_V2
        ) if bot else ...

    except Exception as err:
        logging.exception(err)

from typing import Any, Tuple
from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.formatting import Bold, HashTag, Text, as_list, as_section
from betterlogging import logging

from tgbot.services import broadcaster


logger = logging.getLogger(__name__)


class ReportBuilder():
    def __init__(self, data: dict[str, Any]):
        daytime: str | None = data['daytime'] if 'daytime' in data else None
        location: Text | None = data['location'] if 'location' in data else None
        masters_quantity: str | None = data['masters_quantity'] if 'masters_quantity' in data else None
        latecomers: str | None = data['latecomers'] if 'latecomers' in data else None
        absent: str | None = data['absent'] if 'absent' in data else None
        location_text: Tuple[str] = location.as_kwargs()['text'] if location else (''),

        content = as_list(
            Bold(
                f"{'Утренний отчет ☀️' if daytime == 'morning' else 'Вечерний отчет 🌙'}"
            ),
            HashTag(location_text[0].split('\n')[0].split(': ')[1].replace(' ', '_')),
            location.as_kwargs()['text'] if location else None,
            as_section(
                Bold('Mастеров на смене:'),
                masters_quantity,
                Bold('\nОпоздали:\n\n'),
                latecomers,
                Bold('\nОтсутствуют:\n\n'),
                absent
            )
        )

        self.report = content.as_markdown()

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

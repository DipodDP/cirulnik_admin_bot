# For Pythonanywhere you need to put that into your WSGI configuration file to make background processes work
"""
from background import app as application  # noqa
from background import start_requester_process

url = 'https://' + '.'.join(__name__.split('_')[:-2]) + '.com'
print('URL is: ', url)
start_requester_process(url)
"""

# On PythonAnywhere only the WSGI web app accepts inbound connections and
# uwsgi workers can't run threads, so the bot can't be polled from a worker
# or reached as a subprocess. Instead Telegram POSTs updates to the Flask
# webhook, which hands them over a queue to a long-lived bot process running
# the Dispatcher on one event loop (albums need concurrent update handling).
# The queue and secret are created at WSGI import, in the uwsgi master, so
# every forked worker and the bot process share them.

import asyncio
import hmac
import json
import logging
import secrets
from multiprocessing import Process, SimpleQueue

import requests
from flask import Flask, abort, request

from bot import build_bot, setup_logging
from tgbot.config import load_config
from tgbot.misc.notify_admins import on_startup
from tgbot.misc.setting_comands import set_all_default_commands

WEBHOOK_PATH = '/webhook'
WEBHOOK_SECRET = secrets.token_urlsafe(32)
SECRET_HEADER = 'X-Telegram-Bot-Api-Secret-Token'

app = Flask(__name__)
# ponytail: if the bot process dies, updates pile up until the web app reloads
updates = SimpleQueue()


async def _feed(dp, bot, raw):
    try:
        await dp.feed_raw_update(bot, json.loads(raw))
    except Exception:
        logging.exception('Failed to process update')


async def _run_bot(url):
    config = load_config('.env')
    setup_logging(config.tg_bot.console_log_level)
    bot, dp = build_bot(config)

    await set_all_default_commands(bot)
    await dp.emit_startup(bot=bot, dispatcher=dp, bots=[bot], **dp.workflow_data)
    await bot.set_webhook(url + WEBHOOK_PATH, secret_token=WEBHOOK_SECRET)
    await on_startup(bot, config.tg_bot.admin_ids)

    loop = asyncio.get_running_loop()
    tasks = set()
    while True:
        raw = await loop.run_in_executor(None, updates.get)
        task = asyncio.create_task(_feed(dp, bot, raw))
        tasks.add(task)
        task.add_done_callback(tasks.discard)


def run_bot(url):
    asyncio.run(_run_bot(url))


# Function to make a periodic request
async def request_url_periodically(url, interval):
    while True:
        await asyncio.sleep(interval)
        try:
            response = requests.get(url)
            print(f'Requested {url}, status code: {response.status_code}')
        except Exception as e:
            print(f'Error while requesting {url}: {e}')


# Use multiprocessing to run the async task
def run_periodic_request(url):
    print('Starting the background URL request process')
    interval = 60 * 15  # Time interval in seconds (e.g., every 15 minutes)
    asyncio.run(request_url_periodically(url, interval))


def start_requester_process(url):
    # Start the bot process and the keep-alive requester process
    Process(target=run_bot, args=(url,)).start()
    Process(target=run_periodic_request, args=(url,)).start()


@app.route('/')
def home():
    return '<h1>Bot is alive! :)</h1>'


@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    token = request.headers.get(SECRET_HEADER, '')
    if not hmac.compare_digest(token, WEBHOOK_SECRET):
        abort(403)
    updates.put(request.get_data())
    return '', 200


if __name__ == '__main__':
    app.run()

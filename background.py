# For Pythonanywhere you need to put that into your WSGI configuration file to make background processes work
"""
from background import app as application  # noqa
from background import start_requester_process

url = 'https://' + '.'.join(__name__.split('_')[:-2]) + '.com'
print('URL is: ', url)
start_requester_process(url)
"""

import subprocess
from multiprocessing import Process
from subprocess import Popen
import asyncio

import requests
from flask import Flask, redirect, url_for


app = Flask(__name__)
process: Popen | None = None


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
    # This is the correct way to start an async function with asyncio in a process.
    print('Starting the background URL request thread')
    interval = 60 * 15  # Time interval in seconds (e.g., every 15 minutes)
    asyncio.run(
        request_url_periodically(url + '/start', interval)
    )  # run the coroutine


def start_requester_process(url):
    # Start the background requester process
    requester_process = Process(target=run_periodic_request, args=(url,))
    requester_process.start()  # Start the process


@app.route('/')
def home():
    global process
    if process:
        status = process.poll()
        if status is None:
            result = 'alive! :)'
        else:
            result = f'stopped with code {status}.\
            Press <a href="/start">Start</a>'
    else:
        result = 'down! :(. Press <a href="/start">Start</a>'
    return f'<h1>Bot is {result}</h>'


@app.route('/start')
def start():
    global process
    status = 'Down'
    if process:
        status = process.poll()
    if status is not None:
        # in venv Pythonanywhere you may need to set
        # full path to the Python interpreter
        result_python_path = subprocess.run(
            ['poetry', 'run', 'which', 'python'],
            capture_output=True,
            text=True,
        )
        if result_python_path.returncode == 0:
            python_path = result_python_path.stdout.strip()
        else:
            python_path = 'python'

        # Run main process
        process = subprocess.Popen(f'{python_path} bot.py', shell=True)
        print('Starting...')

    return redirect(url_for('home'))


if __name__ == '__main__':
    start_requester_process('http://127.0.0.1:5000')
    app.run()

import subprocess
import sys
from multiprocessing import Process
from subprocess import Popen
from time import sleep

import requests
from flask import Flask, jsonify, make_response, redirect, request, url_for

from tgbot.core.loader import WEBHOOK_PATH

STARTUP_PATH = '/start'
INTERVAL = 60 * 30  # Time interval in seconds (e.g., every 30 minutes)

app = Flask(__name__)
process: Popen | None = None


def request_startup_url(url):
    """Function to make a startup requests"""
    try:
        response = requests.get(url)
        status_code = response.status_code

        print(f'Requested {url}, status code: {status_code}')

        sleep(5)

        if status_code not in (200, 302):
            request_startup_url(url)

    except Exception as e:
        print(f'Error while requesting {url}: {e}')


def request_url_periodically(url, interval):
    """Function to make a periodic startup requests"""
    request_startup_url(url)
    while True:
        try:
            sleep(interval)
            response = requests.get(url)
            print(f'Requested {url}, status code: {response.status_code}')

        except Exception as e:
            print(f'Error while requesting {url}: {e}')


def start_requester_process(url):
    """
    For Pythonanywhere you need to put this into your WSGI configuration file to run background start process::

    import sys


    # add your project directory to the sys.path
    project_home = '/home/<your_pythonanywhere_username>/<your_project_directory>'
    if project_home not in sys.path:
        sys.path = [project_home] + sys.path

    # import flask app but need to call it "application" for WSGI to work
    from background import app as application  # noqa
    from background import start_requester_process

    url = 'https://' + '.'.join(__name__.split('_')[:-2]) + '.com'
    print('URL is: ', url)
    start_requester_process(url)
    """

    # Create the background requester process
    app.config['url'] = url
    requester_process = Process(
        target=request_url_periodically,
        args=(url + STARTUP_PATH, INTERVAL),
    )
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


# Flask satart subprocess endpoint
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
        process = subprocess.Popen(
            f'{python_path} main.py {app.config.get("url")}', shell=True
        )
        print('Starting...')

    return redirect(url_for('home'))


# Flask webhook endpoint
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook_handler():
    """
    Flask route to proxy webhook requests to Aiogram.
    """

    proxied_response = requests.request(
        method=request.method,  # Forward the same HTTP method
        url=f'http://localhost:8080/{WEBHOOK_PATH}',  # Destination URL
        headers={
            key: value for key, value in request.headers if key != 'Host'
        },
        data=request.get_data(),  # Forward the body
        cookies=request.cookies,  # Forward cookies if needed
    )

    # Return the response from the proxied server
    response = make_response(
        jsonify(proxied_response.json())
        if proxied_response.headers.get('Content-Type') == 'application/json'
        else proxied_response.text
    )
    response.status_code = proxied_response.status_code
    (
        response.headers.add_header(*header)
        for header in proxied_response.headers.items()
    )

    return response


if __name__ == '__main__':
    start_requester_process(sys.argv[1])
    app.run()

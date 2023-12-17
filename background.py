import subprocess
from subprocess import Popen

from flask import Flask, redirect, url_for

app = Flask(__name__)

process: Popen | None = None


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
        # full path to python interpreter
        result_python_path = subprocess.run(
            ['poetry', 'run', 'which', 'python'],
            capture_output=True, text=True)

        if result_python_path.returncode == 0:
            python_path = result_python_path.stdout.strip()
        else:
            python_path = 'python'
        process = subprocess.Popen(f"{python_path} bot.py", shell=True)
        print('Starting...')

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()

import logging
import os.path
import subprocess
import sys
import threading
import time
from typing import Optional

from flask import Flask, redirect
from ._config import set_studio_config
from .handler_charts import charts
from .handler_db_browser import db_browser
from .handler_filesystem import file_system
from .handler_tools import tools
from .config_manager import init_config_manager
from .hotupdate import start_watch_fs
from .. import Config

DIR = os.path.dirname(__file__)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(DIR), 'static'), static_url_path='')
app.register_blueprint(charts, url_prefix="/api/charts")
app.register_blueprint(db_browser, url_prefix="/api/dbBrowser")
app.register_blueprint(file_system, url_prefix="/api/fs")
app.register_blueprint(tools, url_prefix="/api/tools")

_current_runner = None

logger = logging.getLogger(__name__)
@app.route('/')
def handle_root():
    return redirect('http://localhost:8089/index.html', code=301)


class Runner:
    def __init__(self):
        self.p: Optional[subprocess.Popen] = None
        self.th = threading.Thread(target=self.loop)
        self.th.setDaemon(True)
        self.th.start()

    def loop(self):
        self.p = subprocess.Popen([sys.executable, "run.py"], shell=False, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)  # 使用管道
        while self.p.poll() is None:
            line = self.p.stdout.readline().decode("utf8")
            sys.stdout.write(line)

    def stop(self):
        self.p.kill()
        logger.info("Previous runner killed")

def create_runner():
    global _current_runner
    if _current_runner is not None:
        _current_runner.stop()
        time.sleep(1)
    _current_runner = Runner()


def studio_main(config: Config = None):
    """
    Main function for studio server.

    :param config:
    :return:
    """
    set_studio_config(config)
    if config is None:
        conf_folder = os.path.join(os.getcwd(), ".melodiestudio")
    else:
        conf_folder = os.path.join(config.project_root, '.melodiestudio')
    init_config_manager(conf_folder)
    create_runner()
    start_watch_fs(config.project_root, create_runner)

    app.run(host='0.0.0.0', port=8089)

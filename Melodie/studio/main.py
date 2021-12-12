import os.path
from flask import Flask, redirect
from ._config import set_studio_config
from .handler_charts import charts
from .handler_db_browser import db_browser
from .config_manager import init_config_manager
from .. import Config

DIR = os.path.dirname(__file__)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(DIR), 'static'), static_url_path='')
app.register_blueprint(charts, url_prefix="/api/charts")
app.register_blueprint(db_browser, url_prefix="/api/dbBrowser")


@app.route('/')
def handle_root():
    return redirect('http://localhost:8089/index.html', code=301)


def studio_main(conf_folder: str, config: Config = None):
    """
    Main function for studio server.
    :param conf_folder:
    :param config:
    :return:
    """
    set_studio_config(config)
    init_config_manager(conf_folder)

    app.run(port=8089)

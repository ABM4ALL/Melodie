import os.path
from flask import Flask, redirect
from ._config import set_studio_config
from .handler_charts import charts
from .handler_db_browser import db_browser
from .handler_filesystem import file_system
from .handler_tools import tools
from .config_manager import init_config_manager
from .. import Config

DIR = os.path.dirname(__file__)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(DIR), 'static'), static_url_path='')
app.register_blueprint(charts, url_prefix="/api/charts")
app.register_blueprint(db_browser, url_prefix="/api/dbBrowser")
app.register_blueprint(file_system, url_prefix="/api/fs")
app.register_blueprint(tools, url_prefix="/api/tools")


@app.route('/')
def handle_root():
    return redirect('http://localhost:8089/index.html', code=301)


def studio_main(conf_folder: str = '', config: Config = None):
    """
    Main function for studio.rst server.
    :param conf_folder:
    :param config:
    :return:
    """
    set_studio_config(config)
    if conf_folder == '':
        if not os.path.exists('.melodieconfig'):
            os.mkdir(".melodieconfig")
        conf_folder = '.melodieconfig'
    init_config_manager(conf_folder)

    app.run(host='0.0.0.0', port=8089)

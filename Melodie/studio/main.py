import os.path
from flask import Flask
from .handler_charts import charts
from .config_manager import init_config_manager

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello Flask!'


DIR = os.path.dirname(__file__)
app.register_blueprint(charts, url_prefix="/api/charts")


def studio_main(conf_folder):
    """
    Main function for studio server.
    :param cfg_mgr:
    :return:
    """
    init_config_manager(conf_folder)
    app.run(port=8089)

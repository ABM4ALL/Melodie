import os

from Melodie.studio.main import studio_main
from config import config

studio_main(os.path.join(os.getcwd(), ".melodieconfig"), config)

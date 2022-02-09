import sys
import numpy as np
sys.path.append("../..")
from config import config
from model.analyzer import AspirationAnalyzer
from model.plotter import AspirationPlotter

if __name__ == "__main__":
    ana = AspirationAnalyzer(config, plotter_cls=AspirationPlotter)
    ana.run()



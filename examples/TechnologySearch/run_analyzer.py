import sys
import numpy as np
sys.path.append("../..")
from config import config
from model.analyzer import TechnologySearchAnalyzer

if __name__ == "__main__":
    ana = TechnologySearchAnalyzer(config)
    ana.run()



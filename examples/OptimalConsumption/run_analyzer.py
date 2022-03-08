import sys
import numpy as np
sys.path.append("../..")
from config import config
from model.analyzer import OCAnalyzer

if __name__ == "__main__":
    ana = OCAnalyzer(config)
    ana.run()



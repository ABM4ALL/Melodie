import sys
sys.path.append("../..")
from config import config
from model.analyzer import RPSAnalyzer

if __name__ == "__main__":
    ana = RPSAnalyzer(config)
    ana.run()



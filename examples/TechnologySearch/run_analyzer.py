import sys
sys.path.append("../..")
from config import config
from model.analyzer import TechnologySearchAnalyzer

if __name__ == "__main__":
    ana = TechnologySearchAnalyzer(config)
    ana.run()



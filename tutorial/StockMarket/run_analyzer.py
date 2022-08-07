from config import config
from source.analyzer import StockAnalyzer

if __name__ == "__main__":

    analyzer = StockAnalyzer(config)
    analyzer.plot_health_state_share()

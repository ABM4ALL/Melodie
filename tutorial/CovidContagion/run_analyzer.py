from config import config
from source.analyzer import CovidAnalyzer

if __name__ == "__main__":

    analyzer = CovidAnalyzer(config)
    analyzer.plot_health_state_share(id_scenario=0)
    analyzer.plot_health_state_share(id_scenario=1)

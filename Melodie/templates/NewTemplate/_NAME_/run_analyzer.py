
from .config import config
from .analyzer.analyzer import DemoAnalyzerManager
from Melodie import run_analyzer

if __name__ == "__main__":
    run_analyzer(config,
                 analyzer_manager_class=DemoAnalyzerManager
    )
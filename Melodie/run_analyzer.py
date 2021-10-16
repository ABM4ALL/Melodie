
from typing import ClassVar
from .config import NewConfig
from .analyzer_manager import AnalyzerManager

def run_analyzer(config: 'NewConfig',
                 analyzer_manager_class=ClassVar[AnalyzerManager]):
    pass

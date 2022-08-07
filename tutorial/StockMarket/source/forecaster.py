from typing import Callable


class Forecaster:

    def __init__(self,
                 chartist_memory_length: int,
                 fundamentalist_price_benchmark: int):
        self.chartist_memory_length = chartist_memory_length
        self.fundamentalist_price_benchmark = fundamentalist_price_benchmark

    def chartist(self):
        ...

    def fundamentalist(self):
        ...

    def get_rule(self, forecast_rule_id: int) -> Callable:
        if forecast_rule_id == 0:
            return self.chartist
        elif forecast_rule_id == 1:
            return self.fundamentalist
        else:
            raise NotImplementedError(f"Not implemented --> forecast_rule_id = {forecast_rule_id}")




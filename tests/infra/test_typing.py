from typing import Callable, Dict, Any

class Model:
    pass

class DCTestModel(Model):
    pass

def add_custom_collector(row_collector: Callable[[Model], Dict[str, Any]]) -> None:
    # 函数实现
    pass

def my_collector(model: DCTestModel) -> Dict[str, int]:
    # 自定义收集器实现
    pass

add_custom_collector(my_collector)

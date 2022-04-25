import json

from Melodie.basic.vis_charts import ChartManager


def test_chart_manager():
    cm = ChartManager()
    cm.add_chart("chart", ["series1", "series2", "series3"])
    ret = json.dumps(cm.to_json(), indent=4)  # It is fine if json.dumps function does not raise any exception.
    print(ret)
    pass

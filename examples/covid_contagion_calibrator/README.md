# Covid Contagion Calibrator

This example extends the basic `covid_contagion` model and demonstrates
Melodie 的 **Calibrator** 模块：自动搜索 `infection_prob`，使最终感染比例
接近目标值（由 `CalibratorScenarios.csv` 提供）。

## 运行方式

```bash
python examples/covid_contagion_calibrator/main.py
```

## 输入数据
- `SimulatorScenarios.csv`：基础仿真参数（周期数、人数、初始感染率等）。
- `CalibratorScenarios.csv`：校准目标（如 `target_infected_ratio`）。
- `CalibratorParamsScenarios.csv`：GA 搜索参数与取值范围（如 `infection_prob_min/max`）。

## 核心文件
- `core/calibrator.py`：定义校准逻辑和目标函数。
- `core/model.py` / `core/environment.py` / `core/agent.py`：沿用基础 SIR 逻辑。
- `core/scenario.py`：加入 `target_infected_ratio`。
- `core/data_collector.py`：记录宏观 S/I/R 统计及 Agent 状态。

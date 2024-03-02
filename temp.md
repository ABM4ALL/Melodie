1. simulator/calibrator/trainer的输出表格名称，风格与dating market相同

- Result_<驼峰型>
- Result_Simulator_Environment
- Result_Simulator_Men
- Result_Simulator_Women

- Result_Calibrator_EnvironmentCov
- Result_Calibrator_Environment

- Result_Trainer_Players.csv (players为agentlist的变量名)
- Result_Trainer_PlayersCov.csv (players为agentlist的变量名)
- Result_Trainer_Environment.csv
- Result_Trainer_EnvironmentCov.csv

2. input下面的SimulatorScenarios.xlsx，
CalibratorScenarios, TrainerScenarios

3. save_dataframe函数，放在Melodie里面。

4. load_dataframe函数要对calibrator和trainer也生效
- 修改例子的内容，去掉dataloader
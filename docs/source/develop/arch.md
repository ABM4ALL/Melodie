Melodie Architecture
-----
```mermaid
graph TD
sm[ScenarioManager]

model[Model]

al[AgentList]
env[Environment]
dc[DataCollector]
sm -->|Scenario| model %% |遍历每个Scenario,用每一个Scenario初始化模型，然后调用模型实例的run|
model-->al
model-->env
model-->dc %% 需要单独写，在里面写要保存的Agent和Environment的哪些参数。
al-->agent
agent[Agent]
%% agent-.->|globalref|env
env-.->|globalref|al

dc-.->env
dc-.->al
agent-.->env

db[DB]
tg[TableGenerator]
dc-.->db
tg-.->db
model-->tg
```
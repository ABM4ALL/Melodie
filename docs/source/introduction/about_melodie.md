# Introduction to Melodie
Melodie is an Agent-Based Modelling Framework aimed at building, analyzing and tuning models. 

Compared with other ABM frameworks, Melodie implements a Calibrator and a Trainer for model calibration. Besides, Melodie also provides a few ways to speed up both model development and model running.

## The Design Philosophy of Verification
Melodie is designed following the philosophy of **Verification**. There are a lot of assertions and checkings to verify the parameters inside . 

It may be annoying when an error occurs, so we tried our best to raise user-friendly exceptions. Once an error occurs, it will carry a unique id that could be found on [this page](). If you are still confused, you could make an issue on this [Github]() page. 
 
## Concepts in Melodie
There are some important concepts involved in this framework.
- Basic Modelling: 
  - `Agent`, what the system is made up of.
  - `Environment`, where the agents interact with each other
  - `Model`, managing the `Agent`, `Environment`, and other Components including:
    - `AgentContainer` to store agent objects
    - `DataCollector` to collect data
    - `TableGenerator` to generate test data
    - `Grid` and `Network` as space where the agents live
- Scenario and Parameters
  - `Scenario` contains global parameters.
- Manager for Scenarios
  - `Simulator` could run the model within each scenario
  - `Calibrator`
  - `Trainer`
- Management and Visualization
  - Studio. run this command `python -m Melodie studio`, and you will see a webpage with visualization page and some useful tools.
### Running Routine
Melodie modeling needs a Manager to run. The manager can be a `Simulator`, `Calibrator` or `Trainer`. Each `Manager` has a number of `Scenario` to run the `Model` with different parameters.

The `Manager` will iterate through all scenarios, and for each scenario the model will be re-instantiated with current `Scenario`. The `Model` setup its components with parameters from current scenario, and then run.

The running of model consists of discrete steps, and in each step the environment or agent do their actions. After the action, `DataCollector` and `Visualizer` could be used for visualization.

The property of `Environment` and `Agent` are defined in the `setup()` method. It is a good practice to make sure the properties are of  `int`/`float`/`str`/`bool` types, because these types are database friendly. If the Agent or Environment should use complex data structure, please pass them as method arguments.


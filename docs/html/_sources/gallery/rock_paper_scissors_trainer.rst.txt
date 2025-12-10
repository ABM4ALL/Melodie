.. _rock_paper_scissors_trainer:

RockPaperScissorsTrainer
========================

This example demonstrates Melodie's **Trainer** module using a Rock-Paper-Scissors game model.
In this model, agents start with heterogeneous payoff preferences and strategy weights. The trainer then uses a genetic algorithm (GA) to evolve these strategy parameters, aiming for higher accumulated payoffs for each agent.

Trainer: Project Structure
--------------------------

.. code-block:: text

    examples/rock_paper_scissors_trainer
    ├── core/
    │   ├── agent.py            # Defines agent's strategy, actions, and payoff logic
    │   ├── data_collector.py   # Collects micro and macro simulation results
    │   ├── environment.py      # Manages pairwise agent battles
    │   ├── model.py            # Contains the main simulation loop
    │   ├── scenario.py         # Defines scenarios and generates agent parameters
    │   └── trainer.py          # Configures and runs the GA-based training
    ├── data/
    │   ├── input/
    │   │   ├── SimulatorScenarios.csv
    │   │   ├── TrainerScenarios.csv
    │   │   └── TrainerParamsScenarios.csv
    │   └── output/
    └── main.py

Trainer: GA Concepts
--------------------

While the ``Calibrator`` tunes parameters to match an external target, the ``Trainer`` is designed for an **internal** optimization process. Its goal is to allow agents to "learn" and evolve their individual behaviors to maximize their own objectives within the model's world.

**Core Idea: Maximizing Utility**

- **Agent-Level Objective**: Each agent has a goal, which is quantified by a ``utility`` function. In this example, the utility for an agent is its ``accumulated_payoff`` at the end of a simulation run. The Trainer's objective is to find the behavioral parameters that maximize this utility for each agent.
- **Parameters**: You specify which agent-level parameter(s) the Trainer should evolve. Here, it's the three strategy weights: ``strategy_param_1``, ``strategy_param_2``, and ``strategy_param_3``.
- **Utility Function**: You must implement a ``utility(agent)`` method. This function is called after a simulation run and must return a single float value representing that agent's performance or "fitness."

**Genetic Algorithm (GA) for Agent Learning**

The Trainer applies a separate genetic algorithm to *each agent individually*.

- **Chromosome**: An agent's set of trainable parameters (e.g., the three strategy weights) is treated as its "chromosome."
- **Population**: For each agent, the GA maintains a "population" of these chromosomes (i.e., different sets of strategy weights).
- **Fitness**: To evaluate a chromosome, the model is run with the agent using that set of strategy weights. The agent's final ``utility`` (accumulated payoff) serves as the fitness score.
- **Evolution**: Through generations, the GA for each agent independently selects, breeds, and mutates its population of strategy weights, converging on the strategy that yields the highest personal payoff for that agent, given the behavior of all other agents.
- **Parameter Encoding**: The Trainer uses the same binary encoding mechanism as the Calibrator to represent continuous strategy parameters for the GA. For a detailed explanation of this process, please see the *Parameter Encoding: From Float to Binary* section in the :doc:`covid_contagion_calibrator` documentation.

**Parameter Configuration (`TrainerParamsScenarios.csv`)**

This file controls the behavior of the genetic algorithm for all agents:

- ``id``: Unique identifier for a set of GA parameters.
- ``path_num``: How many independent training processes (paths) to run. Each path is a complete run of the GA, helping to test the robustness of the evolutionary outcome.
- ``generation_num``: The number of generations the GA will run for.
- ``strategy_population``: The size of the chromosome population maintained for each agent.
- ``mutation_prob``: The probability of random mutations.
- ``strategy_param_code_length``: The precision of the strategy parameters.
- ``strategy_param_1_min/max``, etc.: These define the search space bounds for each parameter being trained.

Trainer: How It Works
---------------------

- **Simulation Loop**: In each period, agents normalize their strategy weights into action probabilities (rock, paper, or scissors). They are then randomly paired to play one round, and their payoffs are recorded. At the end of the simulation run, each agent's long-term share of actions is calculated.

- **Training Loop**: The ``RPSTrainer`` evolves the strategy parameters for every agent. The **fitness** is each agent's ``accumulated_payoff``. Training settings come from ``TrainerParamsScenarios.csv``.

- **Input Data**: The scenarios for the simulator and trainer are defined in their respective CSV files. Agent-level parameters are generated dynamically within the ``RPSScenario`` class. ``agent_num`` must be an even number, as agents are paired up in each period.

Trainer: Results
----------------

The following plots, taken from the original model, show the evolution of the mean and coefficient of variance for the total accumulated payoff across all agents. This illustrates the effectiveness of the training process.

.. image:: /image/trainer_payoff.png
   :width: 70%
   :align: center
   :alt: Total payoff mean across generations

.. image:: /image/trainer_payoff_cov.png
   :width: 70%
   :align: center
   :alt: Total payoff coefficient of variance across generations

Trainer: Running the Model
--------------------------

You can run both the simulator and the trainer using the main script:

.. code-block:: bash

   python examples/rock_paper_scissors_trainer/main.py

The trainer clears the output directory before it runs. Therefore, after executing the command, you will only find the trainer's output tables in ``examples/rock_paper_scissors_trainer/data/output``. If you need the simulator's results, you should run it separately (for example, by commenting out the ``run_trainer`` call in ``main.py``).

Trainer: Code
-------------

This section shows the key code implementation for the trainer model.

Model Structure
~~~~~~~~~~~~~~~
Defined in ``core/model.py``.

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/model.py
   :language: python
   :linenos:

Environment Logic
~~~~~~~~~~~~~~~~~
Defined in ``core/environment.py``.

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/environment.py
   :language: python
   :linenos:

Agent Behavior
~~~~~~~~~~~~~~
Defined in ``core/agent.py``.

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/agent.py
   :language: python
   :linenos:

Data Collection Setup
~~~~~~~~~~~~~~~~~~~~~
Defined in ``core/data_collector.py``.

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/data_collector.py
   :language: python
   :linenos:

Scenario Definition
~~~~~~~~~~~~~~~~~~~
Defined in ``core/scenario.py``.

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/scenario.py
   :language: python
   :linenos:

Trainer Definition
~~~~~~~~~~~~~~~~~~
Defined in ``core/trainer.py``.

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/trainer.py
   :language: python
   :linenos:


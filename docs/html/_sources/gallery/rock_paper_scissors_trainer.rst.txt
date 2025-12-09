.. _rock_paper_scissors_trainer:

RockPaperScissorsTrainer
========================

This example demonstrates Melodie's **Trainer** module using a Rock-Paper-Scissors game model.
In this model, agents start with heterogeneous payoff preferences and strategy weights. The trainer then uses a genetic algorithm (GA) to evolve these strategy parameters, aiming for higher accumulated payoffs for each agent.

Project Structure (Trainer)
---------------------------

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

How It Works
------------

- **Simulation Loop**: In each period, agents normalize their strategy weights into action probabilities (rock, paper, or scissors). They are then randomly paired to play one round, and their payoffs are recorded. At the end of the simulation run, each agent's long-term share of actions is calculated.

- **Training Loop**: The ``RPSTrainer`` is configured to evolve the ``strategy_param_1``, ``strategy_param_2``, and ``strategy_param_3`` for every agent. The **fitness** of each agent is defined by its ``accumulated_payoff`` at the end of a simulation run. The settings for the training process, such as the number of paths, generations, population size, and mutation rate, are specified in ``TrainerParamsScenarios.csv``.

- **Input Data**: The scenarios for the simulator and trainer are defined in their respective CSV files. Unlike previous examples, the agent-level parameters are not loaded from a static file. Instead, they are generated dynamically within the ``RPSScenario`` class, using the payoff bounds defined in the current scenario. This ensures that each scenario run is based on a distinct, randomly generated but reproducible set of agent parameters. A key requirement for this model is that ``agent_num`` must be an even number, as agents are paired up in each period.

Results
-------

The following plots, taken from the original model, show the evolution of the mean and coefficient of variance for the total accumulated payoff across all agents. This illustrates the effectiveness of the training process.

.. image:: /image/trainer_payoff.png
   :width: 70%
   :align: center
   :alt: Total payoff mean across generations

.. image:: /image/trainer_payoff_cov.png
   :width: 70%
   :align: center
   :alt: Total payoff coefficient of variance across generations

Running the Model
-----------------

You can run both the simulator and the trainer using the main script:

.. code-block:: bash

   python examples/rock_paper_scissors_trainer/main.py

The trainer clears the output directory before it runs. Therefore, after executing the command, you will only find the trainer's output tables in ``examples/rock_paper_scissors_trainer/data/output``. If you need the simulator's results, you should run it separately (for example, by commenting out the ``run_trainer`` call in ``main.py``).

Implementation Details (Trainer)
--------------------------------

Model (`core/model.py`) (RPS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/model.py
   :language: python
   :linenos:

Environment (`core/environment.py`) (RPS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/environment.py
   :language: python
   :linenos:

Agent (`core/agent.py`) (RPS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/agent.py
   :language: python
   :linenos:

Data Collector (`core/data_collector.py`) (RPS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/data_collector.py
   :language: python
   :linenos:

Scenario (`core/scenario.py`) (RPS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/scenario.py
   :language: python
   :linenos:

Trainer (`core/trainer.py`) (RPS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/rock_paper_scissors_trainer/core/trainer.py
   :language: python
   :linenos:


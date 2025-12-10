.. _covid_contagion_calibrator:

CovidContagionCalibrator
========================

This example demonstrates how to use Melodie's **Calibrator** module. It extends the base ``covid_contagion`` model by using a genetic algorithm (GA) to find the value of the ``infection_prob`` parameter that results in a target final infected ratio.

Calibrator: Project Structure
-----------------------------

.. code-block:: text

    examples/covid_contagion_calibrator
    │   ├── core/
    │   │   ├── calibrator.py
    │   │   ├── scenario.py
    │   │   ├── data_collector.py
    │   │   └── model.py
    │   ├── data/
    │   │   ├── CalibratorScenarios.csv
    │   │   └── CalibratorParamsScenarios.csv
    │   └── output/
    └── main.py

Calibrator: Key Changes
-----------------------

The primary changes for the calibrator example are:

- **A ``calibrator.py`` Module**: This new file defines the ``CovidCalibrator`` class, which inherits from ``Melodie.Calibrator``.
- **Calibrator Scenarios**: The input data now includes ``CalibratorScenarios.csv`` and ``CalibratorParamsScenarios.csv`` to control the calibration process. ``CalibratorScenarios.csv`` is similar to ``SimulatorScenarios`` but does not use a ``run_num`` column.
- **Path Modification in ``main.py``**: A special modification to ``sys.path`` is included. This is necessary because the ``Calibrator`` uses multiprocessing for parallel execution. Worker processes are spawned in a new environment and need to be able to find and import the project's modules (e.g., `from examples.covid_contagion_calibrator.core...`). This path modification is a robust way to ensure modules are discoverable when running examples directly from the Melodie repository, which is not a standard installed package.

Calibrator: GA Concepts
-----------------------

The primary goal of the ``Calibrator`` is to automatically tune one or more model parameters to match observed, real-world data. It treats this as an optimization problem: finding the set of parameters that minimizes the "distance" between the model's output and a specified target.

**Core Idea: Minimizing Distance**

- **Target**: You define a target outcome. In this example, the target is for the final proportion of the population that has been infected to be 80%. This target is hard-coded in the ``distance`` function.
- **Parameters**: You specify which scenario parameter(s) the Calibrator should adjust. Here, it's the ``infection_prob``.
- **Distance Function**: You must implement a ``distance(model)`` method. This function is the core of the calibration. It runs after a simulation is complete, calculates a metric from the model's final state, and returns a single float value representing how far off that metric is from the target. The Calibrator's goal is to make this value as close to zero as possible.

**Genetic Algorithm (GA) for Optimization**

Melodie uses a genetic algorithm to search the parameter space efficiently.

- **Chromosome**: A single set of the parameters being calibrated (in this case, just a single value for ``infection_prob``) is treated as a "chromosome."
- **Population**: The GA starts with a "population" of these chromosomes, i.e., many different random values for ``infection_prob``.
- **Fitness**: For each chromosome, the model is run, and the ``distance`` function is calculated. This distance is the fitness score (where lower is better).
- **Evolution**: The GA then proceeds through "generations." In each generation, it selects the best-performing chromosomes (those that produced the smallest distance), "breeds" them (crossover), and introduces random changes (mutation) to create a new population of parameter sets to test. This process iteratively converges toward the parameter set that produces the best fit to the target.

**Parameter Encoding: From Float to Binary**

A key aspect of the genetic algorithm is how it represents continuous parameters like ``infection_prob`` (a float between 0.0 and 1.0). The GA does not work with the float values directly; instead, it converts them into a **binary string** of a fixed length. This process is called discretization.

- **Encoding**: The range of a parameter (e.g., from `infection_prob_min` to `infection_prob_max`) is mapped to a sequence of integers, which are then represented as binary numbers. For instance, a float value is converted into a binary string like ``01101``.
- **GA Operations**: All genetic operations, such as crossover (swapping parts of two binary strings) and mutation (flipping a random bit, e.g., ``01101`` -> ``01111``), are performed on these binary representations.
- **Decoding**: When a simulation needs to be run, the binary string is decoded back into its corresponding float value. This is done in three steps:
    1. The binary string is converted to its decimal integer representation.
    2. This integer is normalized to a float between 0.0 and 1.0 by dividing it by the maximum possible integer for that bit length (which is 2\ :sup:`length` - 1).
    3. This normalized float is linearly mapped to the parameter's defined range (e.g., from `infection_prob_min` to `infection_prob_max`).
- **Precision**: The ``strategy_param_code_length`` parameter in the ``.csv`` file determines the length of this binary string. A longer string allows for a more fine-grained representation of the parameter space (more steps between the min and max bounds), thus offering higher precision at the cost of a larger search space.

**Parameter Configuration (`CalibratorParamsScenarios.csv`)**

This file controls the behavior of the genetic algorithm:

- ``id``: Unique identifier for a set of GA parameters.
- ``path_num``: How many independent calibration processes (paths) to run. Each path is a complete run of the GA from a random start, which helps ensure the result is robust and not just a local minimum.
- ``generation_num``: The number of generations the GA will run for in each path.
- ``strategy_population``: The size of the population in each generation (how many different parameter sets are tested).
- ``mutation_prob``: The probability of a random mutation occurring during breeding.
- ``strategy_param_code_length``: The precision of the parameters, defined by the bit-length of the chromosome.
- ``infection_prob_min``, ``infection_prob_max``: The lower and upper bounds for the ``infection_prob`` parameter search space.

Calibrator: Input Data
----------------------

In this example, the ``distance`` is calculated based on the model's state at the **end of the simulation**. If you need to use data from all periods to calculate the target metric, you can compute and store the required value in an environment property throughout the simulation, ensuring it holds the final desired value at the last period.

Calibrator: Running the Model
-----------------------------

You can run the calibrator using the main script:

.. code-block:: bash

   python examples/covid_contagion_calibrator/main.py

This will execute the genetic algorithm, running multiple simulations in parallel to find the optimal ``infection_prob``. The results, including the progression of parameters and distances across generations, are saved to the ``data/output`` folder.

Calibrator: Code
----------------

This section shows the key code implementation for the calibrator model. Files that are identical to the base ``covid_contagion`` model are noted.

Calibrator Definition
~~~~~~~~~~~~~~~~~~~~~
Defined in ``core/calibrator.py``.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/calibrator.py
   :language: python
   :linenos:

Scenario Definition
~~~~~~~~~~~~~~~~~~~
Defined in ``core/scenario.py``.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/scenario.py
   :language: python
   :linenos:

Model Structure
~~~~~~~~~~~~~~~
*Identical to the base model.* Defined in ``core/model.py``.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/model.py
   :language: python
   :linenos:

Environment Logic
~~~~~~~~~~~~~~~~~
*Identical to the base model.* Defined in ``core/environment.py``.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/environment.py
   :language: python
   :linenos:

Agent Behavior
~~~~~~~~~~~~~~
*Identical to the base model.* Defined in ``core/agent.py``.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/agent.py
   :language: python
   :linenos:

Data Collection Setup
~~~~~~~~~~~~~~~~~~~~~
*Identical to the base model.* Defined in ``core/data_collector.py``.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/data_collector.py
   :language: python
   :linenos:
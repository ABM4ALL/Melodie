CovidContagionCalibrator
========================

This example shows how to use Melodie's **Calibrator** module to tune the
``infection_prob`` parameter of the base ``covid_contagion`` model so that the
final infected ratio matches a target value.

Project Structure (Calibrator)
------------------------------

The layout follows the base example and adds two GA parameter tables plus a
calibrator class:

.. code-block:: text

    examples/covid_contagion_calibrator
    ├── core/
    │   ├── agent.py               # Same SIR agent as base
    │   ├── environment.py         # Infection + recovery logic
    │   ├── model.py               # Simulation loop
    │   ├── scenario.py            # Adds target_infected_ratio for calibration
    │   ├── data_collector.py      # Collects S/I/R counts and agent states
    │   └── calibrator.py          # Defines calibration target and GA hooks
    ├── data/
    │   ├── input/
    │   │   ├── SimulatorScenarios.csv           # Base run parameters
    │   │   ├── CalibratorScenarios.csv          # Calibration scenarios (no run_num)
    │   │   └── CalibratorParamsScenarios.csv    # GA bounds & settings
    │   └── output/
    ├── README.md
    └── main.py                    # Entry point to run the calibrator

Key Differences from Base Model
-------------------------------

1. **Calibrator**: Uses genetic algorithm (GA) to search ``infection_prob``.
2. **Target Metric**: Minimizes the squared gap between the final infected ratio
   and a target (hardcoded as 0.8 in this example).
3. **Extra Inputs**:

   - ``CalibratorScenarios.csv``: Similar to ``SimulatorScenarios.csv`` but defines the scenarios for calibration. It lacks ``run_num`` because the calibrator determines execution paths internally.
   - ``CalibratorParamsScenarios.csv``: GA settings (generations, population,
     mutation rate) and bounds (``infection_prob_min/max``).

Scenario & Input Data
---------------------

- ``SimulatorScenarios.csv``: period/run/agent counts and initial probabilities.
- ``CalibratorScenarios.csv``: defines scenarios for the calibrator (similar to SimulatorScenarios).
- ``CalibratorParamsScenarios.csv``: GA controls and parameter bounds.

Implementation Details
----------------------

Model Setup (`core/model.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This file is identical to the base ``covid_contagion`` model.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/model.py
   :language: python
   :linenos:

Environment Logic (`core/environment.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This file is identical to the base ``covid_contagion`` model.

.. note::

   In this example, the calibration target uses the **end-of-simulation** value of ``num_susceptible``.
   If you want to calibrate based on time-series data or other aggregated metrics, you can calculate
   them in the environment (e.g., in ``update_population_stats``) and store the result in a property.
   As long as the property holds the desired value at the end of the simulation, the Calibrator can access it.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/environment.py
   :language: python
   :linenos:

Agent (`core/agent.py`)
~~~~~~~~~~~~~~~~~~~~~~~

This file is identical to the base ``covid_contagion`` model.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/agent.py
   :language: python
   :linenos:

Scenario (`core/scenario.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/scenario.py
   :language: python
   :linenos:

Data Collector (`core/data_collector.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/data_collector.py
   :language: python
   :linenos:

Calibrator (`core/calibrator.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``CovidCalibrator`` class inherits from ``Melodie.Calibrator``.

Key components:

- ``setup()``: Registers ``infection_prob`` as the tunable parameter via ``add_scenario_calibrating_property``.
- ``distance()``: Defines the error function. Here, it calculates the squared difference between the actual infected ratio and a target (hardcoded as 0.8 in this example).

.. literalinclude:: ../../../examples/covid_contagion_calibrator/core/calibrator.py
   :language: python
   :linenos:

Main Entry (`main.py`)
~~~~~~~~~~~~~~~~~~~~~~

**Note on Import Paths and Multiprocessing**

The ``Calibrator`` module uses Python's ``multiprocessing`` to run simulations in parallel.
For the worker processes to correctly unpickle and import your model classes, the project package must be importable.

1. **Standard Project Structure**:
   If you are developing a standalone project where ``main.py`` is in the project root, and you have installed Melodie via ``pip``, typically no extra path configuration is needed. The current directory is usually implicitly added to ``sys.path``.

2. **Sub-directory / Complex Structure (This Example)**:
   Since this example is nested deep within the Melodie repository (``examples/covid_contagion_calibrator``), the default path behavior might fail for worker processes spawned by ``multiprocessing``.
   
   To fix this, we explicitly insert the project root into ``sys.path`` in ``main.py``. This ensures that statements like ``from examples.covid_contagion_calibrator.core...`` work correctly in both the main process and all worker processes.

.. literalinclude:: ../../../examples/covid_contagion_calibrator/main.py
   :language: python
   :linenos:

Running the Calibrator
----------------------

Run the entry script:

.. code-block:: bash

   python examples/covid_contagion_calibrator/main.py

Outputs (e.g., ``Result_Simulator_Environment.csv`` and GA logs) will appear in
``examples/covid_contagion_calibrator/data/output``.



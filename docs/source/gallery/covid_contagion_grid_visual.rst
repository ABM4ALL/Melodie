.. _covid_contagion_grid_visual:

CovidContagionGridVisual
========================

This example builds upon ``covid_contagion_grid`` by adding a **Visualizer**.
It demonstrates how to use **MelodieStudio** to interactively run the simulation and view real-time animations of the grid and data charts.

Visualizer: Project Structure
-----------------------------

The structure is similar to the grid example but adds a visualizer component:

.. code-block:: text

    examples/covid_contagion_grid_visual
    ├── core/
    │   ├── agent.py
    │   ├── grid.py
    │   ├── environment.py
    │   ├── model.py
    │   ├── scenario.py
    │   ├── visualizer.py       # Defines charts and grid styling
    │   └── ...
    ├── data/
    │   └── ...
    ├── main.py                 # Launches MelodieStudio
    └── ...

Visualizer: Key Changes
-----------------------

1. **Visualizer Class**:
   A new class ``CovidVisualizer`` inherits from ``Melodie.Visualizer``. It defines:

   - **Charts**: A line chart tracking the number of Susceptible, Infected, and Recovered agents.
   - **Grid View**: A visual representation of the grid where agents appear as colored dots (Green=Susceptible, Red=Infected, Gray=Recovered).

2. **MelodieStudio**:
   Instead of running a batch simulation immediately, the ``main.py`` script starts a local web server (MelodieStudio). You can control the simulation (Start, Pause, Reset) from the browser.

Visualizer: Running the Model
-----------------------------

Run the studio server:

.. code-block:: bash

   python examples/covid_contagion_grid_visual/main.py

Then open your browser and visit ``http://localhost:8765``.

- Click the **Simulator** page.
- Select a scenario and click **Start**.
- You will see the grid animation on the left and the health state chart on the right.

Visualizer: Code
----------------

This section shows the key code additions for the visualizer. Core logic files are the same as the ``covid_contagagion_grid`` example.

Visualizer Definition
~~~~~~~~~~~~~~~~~~~~~
This file is the core addition. It maps model data to visual elements. Defined in ``core/visualizer.py``.

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/visualizer.py
   :language: python
   :linenos:

Model Structure
~~~~~~~~~~~~~~~
*Same as the grid example.* Defined in ``core/model.py``.

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/model.py
   :language: python
   :linenos:

Environment Logic
~~~~~~~~~~~~~~~~~
*Same as the grid example.* Defined in ``core/environment.py``.

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/environment.py
   :language: python
   :linenos:

Agent Behavior
~~~~~~~~~~~~~~
*Same as the grid example.* Defined in ``core/agent.py``.

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/agent.py
   :language: python
   :linenos:

Grid Definition
~~~~~~~~~~~~~~~
*Same as the grid example.* Defined in ``core/grid.py``.

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/grid.py
   :language: python
   :linenos:


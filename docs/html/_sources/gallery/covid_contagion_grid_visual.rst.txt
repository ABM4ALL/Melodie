CovidContagionGridVisual
========================

This example builds upon ``covid_contagion_grid`` by adding a **Visualizer**.
It demonstrates how to use **MelodieStudio** to interactively run the simulation and view real-time animations of the grid and data charts.

Project Structure (Visual)
--------------------------

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

Key Differences from Grid Model
-------------------------------

1. **Visualizer Class**:
   A new class ``CovidVisualizer`` inherits from ``Melodie.Visualizer``. It defines:
   
   - **Charts**: A line chart tracking the number of Susceptible, Infected, and Recovered agents.
   - **Grid View**: A visual representation of the grid where agents appear as colored dots (Green=Susceptible, Red=Infected, Gray=Recovered).

2. **MelodieStudio**:
   Instead of running a batch simulation immediately, the ``main.py`` script starts a local web server (MelodieStudio). You can control the simulation (Start, Pause, Reset) from the browser.

Implementation Details (Visual)
-------------------------------

Model Setup (Visual)
~~~~~~~~~~~~~~~~~~~~

*Same as the grid example.*

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/model.py
   :language: python
   :linenos:

Environment Logic (Visual)
~~~~~~~~~~~~~~~~~~~~~~~~~~

*Same as the grid example.*

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/environment.py
   :language: python
   :linenos:

Spatial Agent (Visual)
~~~~~~~~~~~~~~~~~~~~~~

*Same as the grid example.*

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/agent.py
   :language: python
   :linenos:

Grid Definition (Visual)
~~~~~~~~~~~~~~~~~~~~~~~~

*Same as the grid example.*

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/grid.py
   :language: python
   :linenos:

Visualizer Configuration (`core/visualizer.py`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This file is the core addition. It maps model data to visual elements.

.. literalinclude:: ../../../examples/covid_contagion_grid_visual/core/visualizer.py
   :language: python
   :linenos:

Running the Model with Studio
-----------------------------

Run the studio server:

.. code-block:: bash

   python examples/covid_contagion_grid_visual/main.py

Then open your browser and visit ``http://localhost:8765``.

- Click the **Simulator** page.
- Select a scenario and click **Start**.
- You will see the grid animation on the left and the health state chart on the right.


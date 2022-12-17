
CovidContagionVisual
====================

To show how the ``Visualizer`` and ``MelodieStudio`` modules can be used,
we provide two model examples:
`CovidNetworkContagionVisual <https://github.com/ABM4ALL/CovidNetworkContagionVisual>`_ and
`CovidGridContagionVisual <https://github.com/ABM4ALL/CovidGridContagionVisual>`_.
They are both build on top of the `CovidContagion <https://github.com/ABM4ALL/CovidContagion>`_ model,
only with the ``visualizer`` added.
So, if you haven't, we will strongly suggest to read the :ref:`Tutorial` section first.

Visualizer
__________

To visualizer the simulation results, ``Melodie`` provides the module ``visualizer``,
which is optional when constructing the ``simulator``.

.. code-block:: Python
   :caption: run_simulator.py
   :linenos:
   :emphasize-lines: 15, 17-18

   from Melodie import Simulator
   from config import config
   from source.data_loader import CovidDataLoader
   from source.model import CovidModel
   from source.scenario import CovidScenario
   from source.visualizer import CovidVisualizer


   if __name__ == "__main__":
       simulator = Simulator(
           config=config,
           model_cls=CovidModel,
           scenario_cls=CovidScenario,
           data_loader_cls=CovidDataLoader,
           visualizer_cls=CovidVisualizer
       )
       # simulator.run()
       simulator.run_visual()

As shown in Line 15, the ``CovidVisualizer`` is included to construct the ``simulator`` without any other changes.
You can still run the model as before, just by running the ``simulator.run`` function.
But, you can also run the ``simulator.run_visual`` to visualize the simulation results in your browser.
You will see how to play with it in a minute.

MelodieStudio
_____________

``MelodieStudio`` is another package developed in parallel with ``Melodie``,
which interacts with the ``Melodie.Visualizer`` module and visualizes the simulation results in the browser.
You can install it by running ``pip install MelodieStudio`` in the command line.

How to start?
_____________

Taking the ``CovidNetworkContagionVisual`` model as example, you can start the visualization by following the steps as below:

First, run ``python -m MelodieStudio`` in your command line (in "Terminal" if you are using PyCharm).

.. image:: ../image/melodie_studio_start.png

Second, click the first blue link, then in your browser, you will see:

.. image:: ../image/melodie_studio_disconnected.png

Third, as shown, the front-end is started and you can see the ``readme.md`` file of the model.
But, the front-end is still "disconnected" with the back-end.
Now, you go back to the code editor and run the ``simulator.run_visual`` function.
Then, you will see the frond- and back-ends are connected:

.. image:: ../image/melodie_studio_connected.png
   :align: center

Fourth, now, go back to the browser and click the "right triangle", you will see the simulation results.
You can also stop the model or run in steps.
Besides, you can revise the ``infection_prob`` parameter,
then "reset", then start the model again.
The contagion process will be different.

.. image:: ../image/covid_network_contagion_visual.png

The code that produces the figures are all written in the ``visualizer.py`` file as below.

.. code-block:: Python
   :caption: visualizer.py
   :linenos:

   from typing import TYPE_CHECKING
   from Melodie import FloatParam, Visualizer

   if TYPE_CHECKING:
       from source.model import CovidModel


   class CovidVisualizer(Visualizer):
       model: "CovidModel"

       def setup(self):

           self.params_manager.add_param(FloatParam(
               name='infection_prob',
               value_range=(0, 1),
               label="Infection Probability (%)"
           ))

           self.plot_charts.add_line_chart("infection_count_line").set_data_source({
               "not_infected": lambda: self.model.environment.s0,
               "infected": lambda: self.model.environment.s1,
               "recovered": lambda: self.model.environment.s2,
               "dead": lambda: self.model.environment.s3
           })

           self.plot_charts.add_barchart('infection_count_bar').set_data_source({
               "not_infected": lambda: self.model.environment.s0,
               "infected": lambda: self.model.environment.s1,
               "recovered": lambda: self.model.environment.s2,
               "dead": lambda: self.model.environment.s3
           })

           self.add_network(name='covid_contagion_network',
                            lambda: self.model.network,
                            var_getter=lambda agent: agent.health_state,
                            var_style={
                                0: {
                                    "label": "not_infected",
                                    "color": "#00fb34"
                                },
                                1: {
                                    "label": "infected",
                                    "color": "#fafb56"
                                },
                                2: {
                                    "label": "recovered",
                                    "color": "#3434b8"
                                },
                                3: {
                                    "label": "dead",
                                    "color": "#999999"
                                }
                            })

By following same steps, you will also see the visualization of the ``CovidGridContagionVisual`` model:

.. image:: ../image/covid_grid_contagion_visual.png






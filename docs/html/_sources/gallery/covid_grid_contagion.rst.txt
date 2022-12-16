
CovidGridContagion
==================

This `CovidGridContagion <https://github.com/ABM4ALL/CovidGridContagion>`_ model follows the
same structure with the `CovidContagion <https://github.com/ABM4ALL/CovidContagion>`_ model.
The differences are:

* Agents walk on a 2D ``grid`` randomly.
* The ``grid`` is constructed with ``spots``. Each ``spot`` has an attribute ``stay_prob``, which decides if the agent standing on this spot will move probabilistically.
* The infected agents can pass the virus to the other uninfected agents in the neighborhood.




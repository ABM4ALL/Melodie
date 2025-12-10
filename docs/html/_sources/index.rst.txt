
Melodie: Agent-based Modeling in Python
=======================================

**Melodie** is a general framework for developing agent-based models (ABMs) in Python.
Melodie and its example repositories are maintained on `ABM4ALL <https://github.com/ABM4ALL>`_,
a developing community among agent-based modelers for sharing ideas and resources.

The package name **Melodie** comes from an example which poetically explains the core concept of complexity theory: \"`emergence`\".
In his bold book *Emergent Evolution*, `C. Lloyd Morgan <https://en.wikipedia.org/wiki/C._Lloyd_Morgan>`_ wrote:
\"The emergent step, though it may seem more or less saltatory [a leap], is best regarded as a qualitative change of direction,
or critical turning-point, in the course of events.\"
Then, Morgan exemplified how *Melody* emerges from chords by quoting *Abt Vogler* of
`Robert Browning <https://en.wikipedia.org/wiki/Robert_Browning>`_:

| \"And I know not if,
| save in this,
| such gift be allowed to man,
| That out of three sounds he frame,
| not a fourth sound,
| but a star.\"

Sitting in Karlsruhe, a lovely city in southern Germany,
I take the German translation - \"Melodie\" - as the name of this package.

.. image:: image/karlsruhe.png


**Suggested reading path**

* First, you might want to start with the :doc:`introduction` section to get a brief idea what agent-based modeling is about, then an overview of the modules in Melodie and how they fit together.
* Second, you can continue with the :doc:`tutorial` section, in which we explain how an example model (`CovidContagion <https://github.com/ABM4ALL/CovidContagion>`_) is developed with Melodie step by step. It is a minimum example but shows a clear structure and the most important modules in **Melodie**.
* Third, for those who are familiar with `Mesa <https://github.com/projectmesa/mesa>`_ or `AgentPy <https://github.com/JoelForamitti/agentpy>`_, we also provide a comparison between **Melodie** and the two packages in the :doc:`framework_comparison` section. The comparison is done based on the CovidContagion model in the tutorial.
* Fourth, since the tutorial only provides a minimum model developed with Melodie, in the :doc:`gallery/_index`, we provide more example models to show how other modules can be used.
* Finally, the :doc:`API Reference <api/index>` section provides detailed information on all public interfaces.

Now, let's start the journey :)

.. toctree::
   :caption: User Guide
   :maxdepth: 1
   :hidden:

   installation
   introduction
   tutorial
   framework_comparison
   gallery/_index

.. toctree::
   :caption: API Reference
   :maxdepth: 1
   :hidden:

   api/index

.. toctree::
   :caption: Development
   :maxdepth: 1
   :hidden:

   contribution
   changelog
   about

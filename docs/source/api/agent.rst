
Agent
=========

Agent and Environment are all defined in Melodie.boost for better performance, and you may find
it will only jump to a *.pyi* file if you are trying to jump into the code. If you would like to view the source code,
please visit our git repository. The path to related files are listed below:

- Stub File: Melodie/boost/basics.pyi
- Source Code: Melodie/boost/basics.pyx
- Cython Interface: Melodie/boost/basics.pxd

Just include class *Agent* inside doc and undoc the Agent.id and Agent.model

.. autoclass:: Melodie.Agent
    :members:

    .. autoattribute:: id
        :annotation:

        The id of ``Agent``, a integer value ``>=0``

    .. autoattribute:: scenario
        :annotation:

        Current scenario object, of type ``Melodie.Scenario``.

    .. autoattribute:: model
        :annotation:

        The model that this agent belongs to.


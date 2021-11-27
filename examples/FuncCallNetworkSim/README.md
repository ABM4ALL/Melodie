### Example - Function call network simulation

---

This example explores how failure propagate in a software.

A software can be abstracted as a complex network. We regard each function as a node,
and function calls as edges. 

In this model, the graph structure comes from the software of **Lua** Interpreter.

Scenario parameters:

- reliability: The reliability of a function.
- recover_rate: The probability if the failed function could recover.



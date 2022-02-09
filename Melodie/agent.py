from typing import Optional, TYPE_CHECKING

from Melodie.element import Element

if TYPE_CHECKING:
    from Melodie.scenario_manager import Scenario


class Agent(Element):
    def __init__(self, agent_id: int):
        self.id = agent_id
        self.scenario: Optional['Scenario'] = None

    def setup(self):
        """
        This is the initialization method, declare properties here.

        Here, "Declare" is to define properties with zero as initial value, such as:

        ```python
        class NewAgent(Agent)
            def setup(self):
                self.int_property = 0
                self.float_property = 0.0
                self.str_property = ""
        ```

        It is also fine to define properties with complex data structure such as dict/list/set, but the values in the
        complex data structure is hard to be recorded by the `DataCollector`


        This method is executed at the end of the `__init__` method of the corresponding agent container.

        :return:
        """
        pass

    def __repr__(self) -> str:
        d = {k: v for k, v in self.__dict__.items() if
             not k.startswith("_")}
        return "<%s %s>" % (self.__class__.__name__, d)

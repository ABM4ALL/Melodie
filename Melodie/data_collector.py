import logging
import time
from typing import List, TYPE_CHECKING, Dict, Tuple, Any, Optional, Type

import pandas as pd

from MelodieInfra import DBConn, MelodieExceptions

from Melodie.global_configs import MelodieGlobalConfig

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from Melodie import Model, Scenario, BaseAgentContainer


class PropertyToCollect:
    def __init__(self, property_name: str, as_type: Type):
        self.property_name = property_name
        self.as_type = as_type


class DataCollector:
    """
    Data Collector collects data in the model.

    At the beginning of simulation, the ``DataCollector`` creates as the model creates;

    User could customize which property of agents or environment should be collected.

    Before the model running finished, the DataCollector dumps data to dataframe, and save to
    database.
    """

    def __init__(self, target="sqlite"):
        """
        :param target: A string indicating database type, currently just support "sqlite".
        """
        if target not in {"sqlite", None}:
            MelodieExceptions.Data.InvalidDatabaseType(target, {"sqlite"})

        self.target = target
        self.model: Optional[Model] = None
        self.scenario: Optional["Scenario"] = None
        self._agent_properties_to_collect: Dict[str,
                                                List[PropertyToCollect]] = {}
        self._environment_properties_to_collect: List[PropertyToCollect] = []

        self.agent_properties_df = pd.DataFrame()
        self.environment_properties_df = pd.DataFrame()

        self.agent_properties_dict: Dict[str, List[Any]] = {}
        self.environment_properties_list = []

        self._time_elapsed = 0

    def setup(self):
        """
        Setup method, be sure to inherit it.

        :return:
        """
        pass

    def _setup(self):
        self.setup()
        self._time_elapsed = 0

    def time_elapsed(self):
        """
        Get the time spent in data collection.

        :return: Elapsed time, a ``float`` value.
        """
        return self._time_elapsed

    def add_agent_property(
            self, container_name: str, property_name: str, as_type: Type = None
    ):
        """
        This method adds a property of agents in an agent_container to the data collector.

        The type which the data will be represented in the database can also be determined by ``as_type``.

        :param container_name: Container name, also a property name on model.
        :param property_name: Property name on the agent.
        :param as_type: Data type.
        :return:
        """
        if not hasattr(self.model, container_name):
            raise AttributeError(
                f"Model has no agent container '{container_name}'")
        if container_name not in self._agent_properties_to_collect.keys():
            self._agent_properties_to_collect[container_name] = []
        self._agent_properties_to_collect[container_name].append(
            PropertyToCollect(property_name, as_type)
        )

    def add_environment_property(self, property_name: str, as_type: Type = None):
        """
        This method tells the data collector which property of environment should be collected.

        :param property_name: Environment properties
        :param as_type: Data type.
        :return:
        """
        self._environment_properties_to_collect.append(
            PropertyToCollect(property_name, as_type)
        )

    def env_property_names(self) -> List[str]:
        """
        Get the environment property names to collect

        :return: List of environment property names
        """
        return [prop.property_name for prop in self._environment_properties_to_collect]

    def agent_property_names(self) -> Dict[str, List[str]]:
        """
        Get the agent property names to collect

        :return: A ``dict``,  ``<agent_container_name --> agent list properties to gather>[]``
        """
        return {
            container_name: [prop.property_name for prop in props]
            for container_name, props in self._agent_properties_to_collect.items()
        }

    def agent_containers(self) -> List[Tuple[str, "BaseAgentContainer"]]:
        """
        Get all agent containers with attributes to collect in the model.

        :return: A list of tuples, ``<agent_container_name, agent_container_object>[]``
        """
        containers = []
        for container_name in self._agent_properties_to_collect.keys():
            containers.append(
                (container_name, getattr(self.model, container_name)))
        return containers

    def collect_agent_properties(self, period: int, id_run: int, id_scenario: int):
        """
        Collect agent properties.

        :param period: Current simulation step
        :param id_run: Current simulation ``run_id``
        :param id_scenario: Current scenario id
        :return: None
        """
        agent_containers = self.agent_containers()
        agent_property_names = self.agent_property_names()
        for container_name, container in agent_containers:
            agent_prop_list = container.to_list(
                agent_property_names[container_name])
            self.append_agent_properties_by_records(
                container_name, agent_prop_list, period)

    def append_agent_properties_by_records(self, container_name: str, agent_prop_list: List[Dict[str, Any]], period: int):
        """
        Directly append properties to the properties recorder dict.
        If used dynamic-linked-lib as speed up extensions, directly calling this method will be necessary.

        :param period: Current simulation step
        :param container_name: Name of agent container
        :param agent_prop_list: A list with properties as records.
        :return: None
        """
        id_run, id_scenario = self.model.run_id_in_scenario, self.model.scenario.id
        length = len(agent_prop_list)
        props_list = []
        for i in range(length):
            agent_props_dict = agent_prop_list[i]
            tmp_dic = {
                "id_scenario": id_scenario,
                "id_run": id_run,
                "period": period,
                "id": agent_props_dict.pop("id"),
            }
            tmp_dic.update(agent_props_dict)
            props_list.append(tmp_dic)
        if container_name not in self.agent_properties_dict:
            self.agent_properties_dict[container_name] = []
        self.agent_properties_dict[container_name].extend(props_list)

    def append_environment_properties(self, env_properties: Dict[str, Any], period: int):
        env_dic = {
            "id_scenario": self.model.scenario.id,
            "id_run": self.model.run_id_in_scenario,
            "period": period,
        }
        env_dic.update(
            {prop_name: env_properties[prop_name] for prop_name in self.env_property_names()})
        self.environment_properties_list.append(env_dic)

    @property
    def status(self) -> bool:
        """
        If data collector is enabled.

        ``DataCollector`` is only enabled in the ``Simulator``, because ``Trainer`` and ``Calibrator`` are only concerned over
        the properties at the end of the model-running, so recording middle status in ``Trainer`` or ``Calibrator`` is a waste of time and space.

        :return: bool.
        """
        from .simulator import Simulator

        operator = self.model.scenario.manager
        return isinstance(operator, Simulator)

    def collect(self, period: int) -> None:
        """
        The main function to collect data.

        :param period: Current simulation step.
        :return: None
        """
        if not self.status:
            return
        t0 = time.time()

        env_dic = {
            "id_scenario": self.model.scenario.id,
            "id_run": self.model.run_id_in_scenario,
            "period": period,
        }
        env_dic.update(self.model.environment.to_dict(
            self.env_property_names()))

        self.environment_properties_list.append(env_dic)

        

        self.collect_agent_properties(
            period, self.model.run_id_in_scenario, self.model.scenario.id
        )
        t1 = time.time()
        self._time_elapsed += t1 - t0

    @property
    def db(self):
        """
        Create a database connection

        :return: ``melodie.DB`` object.
        """
        return self.model.create_db_conn()

    @staticmethod
    def calc_time(method):
        """
        Works as a decorator.

        If you would like to define a custom data-collect method, please use ``DataCollector.calc_time`` as a decorator.
        """

        def wrapper(obj: DataCollector, *args, **kwargs):
            t0 = time.time()
            ret = method(obj, *args, **kwargs)
            t1 = time.time()
            obj._time_elapsed += t1 - t0
            return ret

        return wrapper

    def get_single_agent_data(self, agent_container_name: str, agent_id: int):
        """
        Get time series data of one agent.

        :param agent_container_name: Attribute name in model.
        :param agent_id: Agent id
        :return:
        """
        container_data = self.agent_properties_dict[agent_container_name]
        return list(filter(lambda item: item['id'] == agent_id, container_data))

    def save(self):
        """
        Save the collected data into database.

        :return: None
        """
        if not self.status:
            return
        t0 = time.time()
        write_db_time = 0
        connection = self.model.create_db_conn()
        environment_properties_df = pd.DataFrame(
            self.environment_properties_list)
        _t = time.time()
        connection.write_dataframe(
            DBConn.ENVIRONMENT_RESULT_TABLE, environment_properties_df, {}
        )
        write_db_time += time.time() - _t

        for container_name in self.agent_properties_dict.keys():
            agent_properties_df = pd.DataFrame(
                self.agent_properties_dict[container_name]
            )
            _t = time.time()
            connection.write_dataframe(
                container_name + "_result", agent_properties_df, {}
            )
            write_db_time += time.time() - _t

        t1 = time.time()
        collect_time = self._time_elapsed
        self._time_elapsed += t1 - t0
        logger.debug(
            f"datacollector took {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s to format dataframe and write it to data.\n"
            f"    {MelodieGlobalConfig.Logger.round_elapsed_time(write_db_time)} for writing into database, and "
            f"{MelodieGlobalConfig.Logger.round_elapsed_time(collect_time)} for collect data."
        )

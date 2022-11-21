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
    """
    It is property to collect.
    stores class and
    """

    def __init__(self, property_name: str, as_type: Type):
        self.property_name = property_name
        self.as_type = as_type


class DataCollector:
    """
    Data Collector collects data for each scenario.
    At the beginning of simulation scenario, the DataCollector creates;
    User could customize which data should be dumped to dataframe.
    By simulation scenario exits, the DataCollector dumps the data to dataframe, and save to
    data or datafile.
    """

    def __init__(self, target="sqlite"):
        if target not in {"sqlite", None}:
            MelodieExceptions.Data.InvalidDatabaseType(target, {"sqlite"})

        self.target = target
        self.model: Optional[Model] = None
        self.scenario: Optional["Scenario"] = None
        self._agent_properties_to_collect: Dict[str, List[PropertyToCollect]] = {}
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

    def time_elapsed(self):
        """
        Get the time spent of collecting data.

        :return:
        """
        return self._time_elapsed

    def add_agent_property(
        self, container_name: str, property_name: str, as_type: Type = None
    ):
        """
        This method tells the data collector which property and in which agent container it should collect.
        It can also be determined what type the data could be represented as in the database.

        :param container_name:
        :param property_name:
        :param as_type:
        :return:
        """
        if not hasattr(self.model, container_name):
            raise AttributeError(f"Model has no agent container '{container_name}'")
        if container_name not in self._agent_properties_to_collect.keys():
            self._agent_properties_to_collect[container_name] = []
        self._agent_properties_to_collect[container_name].append(
            PropertyToCollect(property_name, as_type)
        )

    def add_environment_property(self, property_name: str, as_type: Type = None):
        """
        This method tells the data collector which property of environment should be collected.

        :param property_name:
        :param as_type:
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

        :return: Dictionary agent_container_name --> properties_to_gather[]
        """
        return {
            container_name: [prop.property_name for prop in props]
            for container_name, props in self._agent_properties_to_collect.items()
        }

    def agent_containers(self) -> List[Tuple[str, "BaseAgentContainer"]]:
        """
        Get all agent containers from model.

        :return:
        """
        containers = []
        for container_name in self._agent_properties_to_collect.keys():
            containers.append((container_name, getattr(self.model, container_name)))
        return containers

    def collect_agent_properties(self, period: int, id_run: int, id_scenario: int):
        """
        Collect agent properties.

        :param period:
        :param id_run:
        :param id_scenario:
        :return: None
        """
        agent_containers = self.agent_containers()
        agent_property_names = self.agent_property_names()
        for container_name, container in agent_containers:
            agent_prop_list = container.to_list(agent_property_names[container_name])
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

    @property
    def status(self) -> bool:
        """
        If data collector is enabled.
        Data collector is only enabled in the Simulator, because Trainer and Calibrator are only concerned over
        the properties at the end of the model-running.

        :return: bool.
        """
        from .simulator import Simulator

        operator = self.model.scenario.manager
        return isinstance(operator, Simulator)

    def collect(self, period: int) -> None:
        """
        The main function to collect data.

        :param period:
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
        env_dic.update(self.model.environment.to_dict(self.env_property_names()))

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

        :return:
        """
        return self.model.create_db_conn()

    @staticmethod
    def calc_time(method):
        """
        Works as a decorator.
        If you would like to define a custom data-collect method, please use `DataCollector.calc_time` as a decorator.

        :return:
        """

        def wrapper(obj: DataCollector, *args, **kwargs):
            t0 = time.time()
            ret = method(obj, *args, **kwargs)
            t1 = time.time()
            obj._time_elapsed += t1 - t0
            return ret

        return wrapper

    def save(self):
        """
        Save the collected data into database.

        :return:
        """
        if not self.status:
            return
        t0 = time.time()
        write_db_time = 0
        connection = self.model.create_db_conn()
        environment_properties_df = pd.DataFrame(self.environment_properties_list)
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

import collections
import logging
import os
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generic,
    List,
    NewType,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import pandas as pd
import sqlalchemy

from MelodieInfra import (
    Config,
    DBConn,
    GeneralTable,
    MelodieExceptions,
    Table,
    TableRow,
    is_pypy,
    objs_to_table_row_vectorizer,
)
from MelodieInfra.config.global_configs import MelodieGlobalConfig
from MelodieInfra.utils import underline_to_camel

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from Melodie import AgentList, BaseAgentContainer, Model, Scenario

    M = TypeVar("M", bound=Model)


class PropertyToCollect:
    def __init__(self, property_name: str, as_type: Type):
        self.property_name = property_name
        self.as_type = as_type


VEC_TEMPLATE = """
def vectorize_template(obj):
    return [{exprs}]
"""


def vectorizer(attrs):
    code = VEC_TEMPLATE.format(exprs=",".join([f'obj["{attr}"]' for attr in attrs]))
    d = {}
    exec(code, None, d)
    return d["vectorize_template"]


vectorizers = {}


class DataCollector:
    """
    The DataCollector is responsible for recording data from the model's simulation.

    The DataCollector is initialized by the Model at the beginning of a
    simulation run. It allows users to specify which properties of agents and
    the environment should be collected at each time step.

    At the end of the simulation, the ``save()`` method is called to write the
    recorded data to the specified output format (e.g., CSV files or a SQLite
    database).
    """

    _CORE_PROPERTIES_ = ["id_scenario", "id_run", "period"]

    def __init__(self, target="sqlite"):
        """
        :param target: A string indicating the output format. Supported values
            are "sqlite" (default) and "csv".
        """
        if target not in {"sqlite", "csv", None}:
            MelodieExceptions.Data.InvalidDatabaseType(target, {"sqlite", "csv"})

        self.target = target
        self.config: Optional[Config] = None
        self.model: Optional[Model] = None
        self.scenario: Optional["Scenario"] = None
        self._agent_properties_to_collect: Dict[str, List[PropertyToCollect]] = {}
        self._agent_properties_collectors: Dict[str, Callable[[object], object]] = {}
        self._environment_properties_to_collect: List[PropertyToCollect] = []

        self.agent_properties_dict: Dict[str, Table] = {}
        self.environment_properties_list: Dict[str, Table] = None
        self._custom_collectors: Dict[
            str, Tuple[Callable[[Model], Dict[str, Any]], List[str]]
        ] = {}
        self._custom_collected_data: Dict[str, GeneralTable] = {}

        self._time_elapsed = 0

    def setup(self):
        """
        A hook for setting up the DataCollector.

        This method should be overridden in a subclass to specify which data to
        collect using ``add_agent_property()`` and ``add_environment_property()``.
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
        Register an agent property to be collected from an agent container.

        The data type for the corresponding database column can be explicitly
        defined using ``as_type``.

        :param container_name: The name of the agent container attribute on the
            Model object (e.g., 'agents').
        :param property_name: The name of the property to be collected from each
            agent in the container.
        :param as_type: The desired data type for the database column.
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
        Register an environment property to be collected.

        :param property_name: The name of the property on the Environment object.
        :param as_type: The desired data type for the database column.
        """
        self._environment_properties_to_collect.append(
            PropertyToCollect(property_name, as_type)
        )

    def add_custom_collector(
        self,
        table_name: str,
        row_collector: "Callable[[M], Union[Dict[str, Any], List[Dict[str, Any]]]]",
        columns: List[str],
    ):
        """
        Add a custom data collector to generate a standalone data table.

        :param table_name: The name of the table for storing the collected data.
        :param row_collector: A callable that takes the ``Model`` instance as an
            argument and returns either a dictionary for a single row or a list
            of dictionaries for multiple rows.
        :param columns: A list of column names for the custom table.
        """
        self._custom_collectors[table_name] = (cast(Any, row_collector), columns)

    def env_property_names(self) -> List[str]:
        """
        Get the names of all registered environment properties.

        :return: A list of property names.
        """
        return [prop.property_name for prop in self._environment_properties_to_collect]

    def agent_property_names(self) -> Dict[str, List[str]]:
        """
        Get the names of all registered agent properties, grouped by container.

        :return: A dictionary mapping container names to lists of property names.
        """
        return {
            container_name: [prop.property_name for prop in props]
            for container_name, props in self._agent_properties_to_collect.items()
        }

    def agent_containers(self) -> List[Tuple[str, "BaseAgentContainer"]]:
        """
        Get all agent containers that have properties registered for collection.

        :return: A list of tuples, where each tuple contains the container name
            and the container object itself.
        """
        containers = []
        for container_name in self._agent_properties_to_collect.keys():
            containers.append((container_name, getattr(self.model, container_name)))
        return containers

    def collect_agent_properties(self, period: int):
        """
        (Internal) Collect properties for all registered agent containers.

        :param period: The current simulation period.
        """
        agent_containers = self.agent_containers()
        agent_property_names = self.agent_property_names()
        for container_name, container in agent_containers:
            self.append_agent_properties_by_records(
                container_name, agent_property_names[container_name], container, period
            )

    def collect_custom_properties(self, period: int):
        """
        (Internal) Collect data using all registered custom collectors.

        :param period: The current simulation period.
        """
        for collector_name in self._custom_collectors.keys():
            self.collect_single_custom_property(collector_name, period)

    def collect_single_custom_property(self, collector_name: str, period: int):
        collector_func, column_names = self._custom_collectors[collector_name]
        if collector_name not in self._custom_collected_data:
            self._custom_collected_data[collector_name] = GeneralTable(
                {k: None for k in column_names}, column_names
            )
        assert self.model is not None
        data = collector_func(self.model)
        if isinstance(data, list):
            for item in data:
                assert isinstance(item, dict)
                self._custom_collected_data[collector_name].data.append(item)
        elif isinstance(data, dict):
            self._custom_collected_data[collector_name].data.append(data)
        else:
            raise NotImplementedError(
                "Data collector function should return a list or dict"
            )

    def append_agent_properties_by_records(
        self,
        container_name: str,
        prop_names: List[str],
        container: "AgentList",
        period: int,
    ):
        """
        (Internal) Record properties for a list of agents for the current period.
        """
        assert self.model is not None
        id_run, id_scenario = self.model.run_id_in_scenario, self.model.scenario.id
        if container_name not in self.agent_properties_dict:
            if len(container) == 0:
                raise ValueError(f"No property collected for container {container}!")
            agent_attrs_dict = container.random_sample(1)[0].__dict__
            props = {
                "id_scenario": 0,
                "id_run": 0,
                "period": 0,
                "id": 0,
            }
            props.update({k: agent_attrs_dict[k] for k in prop_names})

            row_cls = TableRow.subcls_from_dict(props)
            self.agent_properties_dict[container_name] = Table(
                row_cls, self._CORE_PROPERTIES_ + ["id"] + prop_names
            )
            self._agent_properties_collectors[
                container_name
            ] = objs_to_table_row_vectorizer(row_cls, prop_names)

        collector = self._agent_properties_collectors[container_name]
        table = self.agent_properties_dict[container_name]
        props_list = table.data
        for agent in container:
            row = collector(table, agent)
            row.id_scenario = id_scenario
            row.id_run = id_run
            row.period = period
            row.id = agent.id
            props_list.append(row)

    def append_environment_properties(self, period: int):
        assert self.model is not None
        assert self.model.environment is not None
        assert self.model.scenario is not None
        env_dic = {
            "id_scenario": self.model.scenario.id,
            "id_run": self.model.run_id_in_scenario,
            "period": period,
        }
        env_dic.update(self.model.environment.to_dict(self.env_property_names()))
        if self.environment_properties_list is None:
            row_cls = TableRow.subcls_from_dict(env_dic)
            self.environment_properties_list = Table(
                row_cls, self._CORE_PROPERTIES_ + self.env_property_names()
            )
        self.environment_properties_list.append_from_dicts([env_dic])

    @property
    def status(self) -> bool:
        """
        Check if the data collector is enabled.

        The ``DataCollector`` is only enabled when running under the ``Simulator``.
        The ``Trainer`` and ``Calibrator`` are typically concerned only with the
        final state of a simulation, so recording time-series data is disabled
        during their execution to improve performance.

        :return: ``True`` if the collector is enabled, otherwise ``False``.
        """
        from .simulator import Simulator

        operator = self.model.scenario.manager
        return isinstance(operator, Simulator)

    def collect(self, period: int) -> None:
        """
        The main data collection method, called by the ``Simulator`` at each step.

        :param period: The current simulation period.
        """
        if not self.status:
            return
        t0 = time.time()
        self.append_environment_properties(period)
        self.collect_agent_properties(period)
        self.collect_custom_properties(period)
        t1 = time.time()

        self._time_elapsed += t1 - t0

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
        return list(filter(lambda item: item["id"] == agent_id, container_data))

    def _write_list_to_table(
        self, engine, table_name: str, data: Union[Table, GeneralTable]
    ):
        """
        (Internal) Write a data table to the specified output (CSV or database).
        """
        if self.model.config.data_output_type == "csv":
            base_path = self.model.config.output_tables_path()
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            path = os.path.join(base_path, table_name + ".csv")
            data.to_file(path)
        else:
            data.to_database(engine, table_name)

    def save(self):
        """
        Save all collected data to the specified output (CSV files or database).
        """
        if not self.status:
            return
        t0 = time.time()
        write_db_time = 0
        assert self.model is not None
        connection = self.model.create_db_conn()

        _t = time.time()
        if self.environment_properties_list is not None:
            self._write_list_to_table(
                connection.get_engine(),
                DBConn.ENVIRONMENT_RESULT_TABLE,
                self.environment_properties_list,
            )
        self.environment_properties_list = None
        write_db_time += time.time() - _t

        for container_name in self.agent_properties_dict.keys():
            _t = time.time()
            self._write_list_to_table(
                connection.get_engine(),
                "Result_Simulator_" + underline_to_camel(container_name),
                self.agent_properties_dict[container_name],
            )
            write_db_time += time.time() - _t

        for custom_table_name in self._custom_collected_data.keys():
            _t = time.time()
            self._write_list_to_table(
                connection.get_engine(),
                custom_table_name,
                self._custom_collected_data[custom_table_name],
            )
            write_db_time += time.time() - _t
        self.agent_properties_dict = {}

        t1 = time.time()

        collect_time = self._time_elapsed
        self._time_elapsed += t1 - t0
        logger.debug(
            f"datacollector took {MelodieGlobalConfig.Logger.round_elapsed_time(t1 - t0)}s to format dataframe and write it to data.\n"
            f"    {MelodieGlobalConfig.Logger.round_elapsed_time(write_db_time)} for writing into database, and "
            f"{MelodieGlobalConfig.Logger.round_elapsed_time(collect_time)} for collect data."
        )
        connection.close()

    def save_dataframe(self, df: pd.DataFrame, df_name: str, if_exists: str = "append"):
        """
        A utility method to save a pandas DataFrame to a CSV file in the
        output directory.

        :param df: The pandas DataFrame to save.
        :param df_name: The desired name for the output file (without extension).
        :param if_exists: What to do if the file already exists. Can be
            'append', 'replace', or 'fail'.
        """
        path = os.path.join(self.config.output_folder, f"{df_name}.csv")
        if os.path.isfile(path):
            if if_exists == "append":
                df.to_csv(path, mode="a", header=False, index=False)
            elif if_exists == "replace":
                df.to_csv(path, index=False)
            else:
                raise NotImplementedError(
                    f"if_exists = {if_exists} --> not implemented."
                )
        else:
            df.to_csv(path, index=False)

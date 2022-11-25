from collections import Counter
from typing import TYPE_CHECKING, Any, List, Callable, Dict, Set

if TYPE_CHECKING:
    from Melodie import Agent


def assert_exc_occurs(exc_id: int, func: Callable):
    """
    Assert that this exception will occur.
    """
    try:
        func()
        assert False
    except MelodieException as e:
        import traceback
        traceback.print_exc()
        assert e.id == exc_id


def assert_exc_type_occurs(exc_type: BaseException, func: Callable):
    """
    Assert that exception of `exc_type` must occur.

    """
    try:
        func()
        assert False
    except BaseException as e:
        import traceback
        traceback.print_exc()
        assert isinstance(e, exc_type)


class MelodieException(Exception):
    def __init__(self, exc_id: int, text: str):
        text = f"{text} <Error ID {exc_id}>"
        super(MelodieException, self).__init__(text)
        self.id = exc_id


class MelodieExceptions:
    class Assertions:
        @staticmethod
        def Type(name, obj, expected_type):
            """
            Assert that the type of `obj` is the `expected_type`.
            """
            if not isinstance(obj, expected_type):
                raise MelodieExceptions.General.TypeError(name, obj, expected_type)

        @staticmethod
        def IsNone(name, obj):
            """
            Assert variable `obj` is None.

            """
            if obj is not None:
                raise TypeError(f"{name} should be None, however it is not None.")

        @staticmethod
        def NotNone(name, obj):
            """
            Assert that the `obj` is not None
            """
            if obj is None:
                raise TypeError(f"{name} should not be None, however it is None.")

    class General:
        @staticmethod
        def TypeError(name, obj, expected_type: type):
            """
            The encapsulation of TypeError
            """
            return TypeError(
                f"{name} should be a {expected_type}, however it was {type(obj)}, value {obj}"
            )

        @staticmethod
        def NoAttributeError(obj, attr_name: str):
            """
            The encapsulation of AttributeError
            """
            return AttributeError(f"Object {obj} has no attribute {attr_name}")

    class Program:
        """
        Errors related to programming

        * code: 1000
        """

        ID = 1000

        class Variable:
            ID = 1010

            @staticmethod
            def VariableInvalid(var_desc: str, var_value: Any, expected_value: Any):
                """
                If this occurs, please check the value of variable

                * code: 1011
                """
                return MelodieException(
                    1011,
                    f"Variable {var_desc} is {var_value}, but expected {expected_value} ",
                )

            @staticmethod
            def VariableNotInSet(var_desc: str, var_value: Any, allowed_set: Set[Any]):
                """
                Please check if variable is in the allowed set.

                * code: 1012
                * example: If the allowed set is {"apple", "pears"}, but the variable value is "banana"
                """
                return MelodieException(
                    1012,
                    f"Variable {var_desc} is {var_value}, not in allowed set {allowed_set} ",
                )

        class Function:
            ID = 1020

            @staticmethod
            def FunctionArgsNumError(
                    func: Callable, expected_arg_num: int, actual_arg_num: int
            ):
                """
                Function should have correct number of arguments. If not, this error will be raised.

                * code: 1021
                * example: Expecting 1 argument, but the function was ``lambda a, b: a+b``
                """
                return MelodieException(
                    1021,
                    f"There should be {expected_arg_num} for function {func}, "
                    f"but the actual argument number was {actual_arg_num}",
                )

    class State:
        ID = 1100

        @staticmethod
        def StateNotFoundError(state, all_states):
            """ """
            return MelodieException(
                1101,
                f"State {repr(state)} is not defined. All states are: {all_states}",
            )

        @staticmethod
        def CannotMoveToNewStateError(
                old_state, new_state, all_possible_new_states: set
        ):
            if len(list(all_possible_new_states)) == 0:
                return MelodieException(
                    1102,
                    f"Current state is {repr(old_state)}, on which the status could only move to"
                    f" itself. However the new state was {repr(new_state)}",
                )
            else:
                return MelodieException(
                    1102,
                    f"Current state is {repr(old_state)}, on which the status could only move to"
                    f" {all_possible_new_states}. However the new state was {repr(new_state)}",
                )

        @staticmethod
        def NotAStateAttributeError(agent_cls, state_attr: str):
            return MelodieException(
                1103, f"Class {agent_cls} has not defined state attribute {state_attr}"
            )

    class Scenario:
        ID = 1200

        @staticmethod
        def ScenarioIDDuplicatedError(id_scenario):
            """
            Scenario ID should be unique. If there are identical scenario-id in the scenario table or generated,
            this error will be raised.

            * code: 1201
            * example: The scenario table below could make this error occur.

            .. list-table:: Scenarios
               :widths: 25 25 25 25
               :header-rows: 1

               * - ID
                 - env_param_1
                 - env_param_2
                 - ...
               * - 0
                 - 10
                 - 20
                 - ...
               * - 0
                 - 15
                 - 20
                 - ...

            In this table, the ids of scenarios are identical, which will cause this exception.

            """
            return MelodieException(
                1201, f"Scenario id {id_scenario} was duplicated, which is not allowed."
            )

        @staticmethod
        def ScenarioIDTypeError(id_scenario):
            """
            Scenario ID should be integer type.

            * code: 1202
            * hint: Please check carefully to make sure the scenario id is integer.
            """
            return MelodieException(
                1202,
                f"Scenario id {id_scenario} should be int. However its type was {type(id_scenario)}.",
            )

        @staticmethod
        def NoValidScenarioGenerated(scenarios):
            """
            Operators (Simulator/Trainer/Calibrator) will generate a list of scenarios.
            If no scenario has been generated, this error will be raised.

            * code: 1204

            Hint:

            * If you overrode the ``generate_scenarios`` method of DataframeLoader, make sure valid value returned.
            * If you are using ``xlsx`` tables, make sure the first page of ``<operator_type>_scenarios.xlsx``
              is not empty.

            """
            return MelodieException(
                1204,
                f"The scenario manager has not generated any valid scenarios. "
                f"The scenarios generated by gen_scenarios() was {scenarios},"
                f"please make sure gen_scenarios() returns a list of Scenario.",
            )

        @staticmethod
        def ParameterRedefinedError(parameter_name: str, all_params: List):
            """
            For the interactive parameters of Scenario, the name should be unique.
            If two parameters has the same name, this exception will be raised.

            * code: 1205
            """
            return MelodieException(
                1205,
                f'A parameter with same name "{parameter_name}" already existed! all parameters are: {all_params}',
            )

    class Agents:
        ID = 1300

        @staticmethod
        def AgentListEmpty(agent_manager):
            """
            * code: 1301
            """
            return MelodieException(
                1301, f"Agent manager {agent_manager} contains no agents!"
            )

        @staticmethod
        def AgentPropertyNameNotExist(property_name, agent):
            """
            * code: 1302
            """
            return MelodieException(
                1302,
                f"Agent {agent} does not have property {property_name}.",
            )

        @staticmethod
        def AgentIDConflict(agent_container_name: str, agent_ids: List[int]):
            """
            Agent ID should be unique.

            * code: 1303
            """
            c = Counter(agent_ids)
            duplicated_ids = [
                agent_id for agent_id, times in c.most_common() if times > 1
            ]

            return MelodieException(
                1303,
                f"Agent container `{agent_container_name}` has duplicated agent IDs: {duplicated_ids}.",
            )

    class Environment:
        ID = 1400

    class Data:
        """
        This class is used when external data is imported or exported.
        """

        ID = 1500

        @staticmethod
        def TableNameAlreadyExists(table_name: str, existed: str):
            return MelodieException(
                1501,
                f"Table Named {table_name} does not exist. All existed tables are: {existed}",
            )

        @staticmethod
        def StaticTableNotRegistered(table_name: str, all_table_names: List[str]):
            """
            Static table should be registered before use.

            * code: 1502
            * hint: Make sure this table is correctly registered in the DataLoader.
            """
            return MelodieException(
                1502,
                f"Table '{table_name}' is not registered. All registered tables are: {all_table_names}.",
            )

        @staticmethod
        def AttemptingReadingFromUnexistedTable(table_name):
            """
            When reading the database, the table must exist in the database.
            * code: 1503
            """
            return MelodieException(1503, f"Table '{table_name}' does not in database.")

        @staticmethod
        def ObjectPropertyTypeUnMatchTheDataFrameError(
                param_name: str,
                param_type: type,
                dataframe_dtypes: Dict[str, type],
                agent: "Agent",
        ):
            """
            Object type should match the type defined in dataframe.

            * code: 1504
            * example: If the dataframe has type float, and agent property was str.
            """
            return MelodieException(
                1504,
                f"The Agent property '{param_name}' is of type {param_type}, but the corresponding column "
                f"of the dataframe is of type {dataframe_dtypes[param_name]}.\n"
                f"The agent that offended is: {agent}",
            )

        @staticmethod
        def TableNameInvalid(table_name):
            """
            The table name should be an identifier.

            * code: 1505
            * hint: Do not use "+", "-", "*", "/" or other special characters.
            * example: ``table-123``; ``table+123``
            """
            return MelodieException(
                1505,
                f"Table name '{table_name}' is invalid."
                f"The expected table name should be an identifier.",
            )

        @staticmethod
        def TableNotFound(table_name: str, all_tables: dict):
            """
            Table may not be registered.

            * code: 1506

            """
            return MelodieException(
                1506,
                f"Table '{table_name}' is not found. All registered tables are: {set(all_tables.keys())}",
            )

        @staticmethod
        def InvalidDatabaseType(database: str, supported_db_types: Set[str]):
            """
            * code: 1508
            """
            return MelodieException(
                1508,
                f"Melodie only support these kinds of databases: {supported_db_types}.\n"
                f"Database type {database} is not supported right now.\n"
                "Is there any spelling problems with the database name?\n"
                "If you do not need to write data into database, please pass `None` as DB type.",
            )

        @staticmethod
        def NoDataframeLoaderDefined():
            """
            Dataframe Loader must be defined if you want to use the static table.

            * code: 1509
            """
            return MelodieException(
                1509,
                f"No dataframe loader defined for the Simulator/Calibrator/Trainer.",
            )

        @staticmethod
        def ColumnNameConsistencyError(
                df_name: str, missing: Set[str], undefined: Set[str]
        ):
            """
            The column name in code should be consistent to the table.

            * code: 1510
            """
            return MelodieException(
                1510,
                f"Column name inconsistent: '{df_name}'\n"
                + ("" if len(missing) == 0 else f"Missing columns: {missing}\n")
                + ("" if len(undefined) == 0 else f"Undefined columns: {undefined}"),
            )

    class Tools:
        """
        This class is for errors related to dev tools such as MelodieStudio
        """

        ID = 1600

        @staticmethod
        def MelodieStudioUnAvailable():
            """
            Melodie studio must be started before visualizer process start.

            * code: 1601
            """
            return MelodieException(
                1601,
                f"Connection to Melodie Studio was refused. It seems that Melodie studio is not "
                f"started yet. Please start Melodie Studio.",
            )

    class Visualizer:
        """
        This class is for errors related to visualizer.
        """

        ID = 1700

        class Charts:
            ID = 1700

            @staticmethod
            def ChartNameAlreadyDefined(chart_name: str, all_chart_names: List[str]):
                """
                * code: 1701
                """
                return MelodieException(
                    1701,
                    f"Chart name '{chart_name}' is already defined. All chart names are: {all_chart_names}",
                )

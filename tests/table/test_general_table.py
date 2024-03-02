import os
import time

from base import OUTPUT_DIR
from sqlalchemy import Integer

from MelodieInfra.table import GeneralTable

XLSFILE = os.path.join(os.path.dirname(__file__), "data", "params.xlsx")

XLSFILE_TO_WRITE = os.path.join(OUTPUT_DIR, "params.xlsx")
CSVFILE_TO_WRITE = os.path.join(OUTPUT_DIR, "params.csv")
SQLITE_FILE = os.path.join(OUTPUT_DIR, "out.sqlite")


def test_create_table():
    table = GeneralTable.from_dicts(
        {"a": Integer(), "b": Integer()}, [{"a": i, "b": i} for i in range(1000)]
    )

    row = table.find_one(lambda obj: obj["a"] == 999)
    assert row is not None
    assert row["a"] == 999


def test_load_table():
    table = GeneralTable.from_file(XLSFILE, {})
    print(table.data[-1])


def test_write_table():
    l = ["a", "b", "c", "d", "__e", "f", "g"]
    table = GeneralTable.from_dicts(
        {k: Integer() for k in l}, [{k: i for k in l} for i in range(2000)]
    )
    t0 = time.time()
    table.to_file(CSVFILE_TO_WRITE)

    t1 = time.time()
    print("write_table_time", t1 - t0)


class Agent:
    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b


# def collect(agents: List[Agent], props: List[str], table: GeneralTable):
#     table.data = []
#     for agent in agents:
#         r = table.row_cls(**{prop_name: getattr(agent, prop_name)
#                              for prop_name in props})
#         table.data.append(r)


# def collect2(agents: List[Agent], collector, table: GeneralTable):
#     table.clear()
#     for agent in agents:
#         table.data.append(collector(agent, table))


# collector_template = """
# def collector3(a, table:GeneralTable):
#     r = table.new_row()
# {assignments}
#     return r
# """


# def create_collector(properties: List[str]):
#     code = collector_template.format(assignments="\n".join(
#         ["    "+f"r.{prop} = a.{prop}" for prop in properties]))
#     local_vars = {}
#     exec(code, None, local_vars)
#     return local_vars['collector3']


# def test_to_database():
#     print("to_database")
#     engine = create_engine("sqlite:///" + SQLITE_FILE)
#     print("engine created")
#     agents = [{"a": i, "b": i} for i in range(1000)]
#     table = GeneralTable.from_dicts({"a": Integer(), "b": Integer()}, agents)
#     # table.from_dicts()
#     print("table")
#     table.to_database(engine, "aaaaaa")
#     print("table")
#     table.from_database(engine, "aaaaaa", "select * from aaaaaa")
#     print("table")


def test_indicing():
    print("indicing")
    agents = [{"a": i, "b": i} for i in range(1000)]
    table = GeneralTable.from_dicts({"a": Integer(), "b": Integer()}, agents)
    assert table.at[50, "a"] == 50
    assert table.iat[50, 0] == 50

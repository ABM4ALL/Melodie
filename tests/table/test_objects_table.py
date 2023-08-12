from dataclasses import dataclass
import os
import time
from typing import List
from base import OUTPUT_DIR
from MelodieInfra.table import Table, TableRow, column_meta
from sqlalchemy import BigInteger, Integer, create_engine

XLSFILE = os.path.join(os.path.dirname(__file__), "data", "params.xlsx")

XLSFILE_TO_WRITE = os.path.join(OUTPUT_DIR, "params.xlsx")
CSVFILE_TO_WRITE = os.path.join(OUTPUT_DIR, "params.csv")
SQLITE_FILE = os.path.join(OUTPUT_DIR, "out.sqlite")


class TableRowType1(TableRow):
    a: int
    b: int = column_meta("b", Integer())


def test_create_table():
    print(TableRowType1.get_datatypes())
    assert type(TableRowType1.get_datatypes()["a"].type) == BigInteger
    assert type(TableRowType1.get_datatypes()["b"].type) == Integer

    table = Table.from_dicts(TableRowType1, [{"a": i, "b": i} for i in range(1000)])

    row = table.find_one(lambda obj: obj.a == 999)
    assert row is not None
    assert row.a == 999


class TableRowType2(TableRow):
    a: int = column_meta("**a")
    b: int = column_meta("^&1b", Integer())


def test_create_with_alias():
    assert type(TableRowType2.get_datatypes()["a"].type) == BigInteger
    assert type(TableRowType2.get_datatypes()["b"].type) == Integer

    table = Table.from_dicts(TableRowType2, [{"**a": i, "^&1b": i} for i in range(100)])
    print(table.data)
    row = table.find_one(lambda obj: obj.a == 99)
    assert row is not None
    assert row.a == 99


class RowToLoad(TableRow):
    id: int
    id_sector: int
    id_sector_agent: int
    forecast_technical_weight: float
    inv_1: float
    inv_2: float
    inv_3: float
    inv_4: float
    tra_1: float
    tra_2: float
    tra_3: float
    tra_4: float


def test_load_table():
    table = Table.from_file(XLSFILE, RowToLoad)
    print(table.data[-1])


class TableRowCls4WriteTable(TableRow):
    a: int
    b: int
    c: int
    d: int
    _e: int
    f: int
    g: int


def test_write_table():
    l = ["a", "b", "c", "d", "_e", "f", "g"]
    table = Table.from_dicts(
        TableRowCls4WriteTable, [{k: i for k in l} for i in range(2000)]
    )
    t0 = time.time()
    table.to_file_with_codegen(CSVFILE_TO_WRITE)

    t1 = time.time()
    print("write_table_time", t1 - t0)


class Agent:
    def __init__(self, a, b) -> None:
        self.a = a
        self.b = b


def collect(agents: List[Agent], props: List[str], table: Table):
    table.data = []
    aliases = table.row_cls.get_aliases()
    for agent in agents:
        r = table.row_cls.from_dict(
            table,
            {prop_name: getattr(agent, prop_name) for prop_name in props},
            aliases,
        )
        table.data.append(r)


def collect2(agents: List[Agent], collector, table: Table):
    table.clear()
    for agent in agents:
        table.data.append(collector(agent, table))


collector_template = """
def collector3(a, table:Table):
    r = table.row_cls(table)
{assignments}
    return r
"""


def create_collector(properties: List[str]):
    code = collector_template.format(
        assignments="\n".join(["    " + f"r.{prop} = a.{prop}" for prop in properties])
    )
    local_vars = {}
    exec(code, None, local_vars)
    return local_vars["collector3"]


def test_to_database():
    engine = create_engine("sqlite:///" + SQLITE_FILE)
    agents = [{"a": i, "b": i} for i in range(1000)]
    table = Table.from_dicts(TableRowType1, agents)
    # table.from_dicts()

    table.to_database(engine, "aaaaaa")


def test_data_collect():
    agents = [Agent(i, i * 2) for i in range(1000)]
    table = Table(TableRowType1)
    # print(create_collector(["a", "b"]))

    def collector3(a, table: Table):
        r = table.row_cls(table)
        r.a = a.a
        r.b = a.b
        return r

    N = 100
    t0 = time.time()
    for i in range(N):
        collect(agents, ["a", "b"], table)
    t1 = time.time()
    table.row_cls
    for i in range(N):
        collect2(agents, lambda a, table: table.row_cls(table, a=a.a, b=a.b), table)
    t2 = time.time()
    for i in range(N):
        collect2(agents, collector3, table)
    t3 = time.time()
    collector_func = create_collector(["a", "b"])
    for i in range(N):
        collect2(agents, collector_func, table)
    t4 = time.time()
    print(t1 - t0, t2 - t1, t3 - t2, "dynamically-created-collector", t4 - t3)


def test_indicing():
    agents = [{"a": i, "b": i} for i in range(1000)]
    table = Table.from_dicts(TableRowType1, agents)
    assert table.iat[50, "a"] == 50


def test_create_autodetect():
    agents = [{"a": i, "b": i + 0.5} for i in range(1000)]
    row_cls = TableRow.subcls_from_dict(agents[0])
    table = Table.from_dicts(row_cls, agents)

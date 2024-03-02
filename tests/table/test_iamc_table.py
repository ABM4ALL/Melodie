import os

from MelodieInfra.table import PyAMTable, PyAMTableRow

# if not is_pypy():
#     import pyam
PATH = os.path.join(os.path.dirname(__file__), "data", "pyam_tutorial_data.csv")


class CurrPyAMRow(PyAMTableRow):
    Model: str


def test_filter():
    table: PyAMTable[CurrPyAMRow] = PyAMTable.from_file(PATH, {})

    new_table = table.filter(lambda row: row.Model.startswith("MESSAGE"))
    print(new_table.find_one_with_index(lambda obj: True))


def test_create_table():
    table = PyAMTable.from_file(
        os.path.join(os.path.dirname(__file__), "data", "pyam_tutorial_data.csv"), {}
    )
    assert len(table) == 1026

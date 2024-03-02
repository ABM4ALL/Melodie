import pandas as pd

from MelodieInfra.table import Table, TableInterface, TableRow


def filter_test(df, table):
    table_filtered = TableInterface(table).filter(lambda row: row["a"] == 1)
    assert len(table_filtered) == 3

    pd_filtered = TableInterface(df).filter(lambda row: row["a"] == 1)
    assert len(pd_filtered) == 3


def iter_test(df, table):
    # interface = TableInterface(ddf)
    table_rows = [r for r in TableInterface(table).iter_dicts()]
    df_rows = [r for r in TableInterface(df).iter_dicts()]
    assert len(table_rows) == len(df_rows)


def test_filter():
    data = [[1, 2, 3], [1, 2, 4], [1, 3, 5], [2, 3, 4], [2, 4, 6]]
    df = pd.DataFrame(data, columns=["a", "b", "c"])

    class MyRow(TableRow):
        a: int
        b: int
        c: int

    table = Table.from_dicts(
        MyRow, [{"a": item[0], "b": item[1], "c": item[2]} for item in data]
    )

    filter_test(df, table)
    iter_test(df, table)

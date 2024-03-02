from MelodieInfra import Table, TableRow, objs_to_table_row_vectorizer


class CustomClass:
    def __init__(self, a, b, c) -> None:
        self.a = a
        self.b = b
        self.c = c


class MyTableRow(TableRow):
    a: int
    b: float


def test_vectorizer():
    table = Table(MyTableRow)
    vectorizer = objs_to_table_row_vectorizer(MyTableRow, ["a", "b"])
    original_obj_list = [CustomClass(i, i + 1, i + 2) for i in range(10)]
    print([vectorizer(table, item) for item in original_obj_list])

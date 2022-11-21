from Melodie import DataFrameInfo
from sqlalchemy import Integer
from MelodieInfra.exceptions.exceptions import assert_exc_occurs

df_info = DataFrameInfo("df_name", {"a": Integer(), "b": Integer(), "c": Integer()})


def test_data_info_column_error():
    assert_exc_occurs(1510, lambda: df_info.check_column_names(["a", "b"]))
    assert_exc_occurs(1510, lambda: df_info.check_column_names(["a", "b", "c", "d"]))
    assert_exc_occurs(1510, lambda: df_info.check_column_names(["a", "b", "d"]))

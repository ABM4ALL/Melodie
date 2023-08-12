import csv

from typing import (
    Callable,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    Dict,
    cast,
)
from sqlalchemy import Column
from sqlalchemy.types import TypeEngine
from sqlalchemy.orm import declarative_base
from .reader_writer import TableReader
from .table_base import TableBase, RowBase

Base = declarative_base()


class PyAMTableRow(RowBase):
    def __init__(self, **kwargs) -> None:
        self.data: List[float] = []
        for k, v in kwargs.items():
            setattr(self, k, v)


class PyAMKey:
    def __init__(self, name: str, col_index: int) -> None:
        self.name = name
        self.col_index = col_index


RowType = Union[Type, Dict[str, TypeEngine]]

PyAMTableRowType = TypeVar("PyAMTableRowType")


class PyAMTable(TableBase, Generic[PyAMTableRowType]):
    data: List[PyAMTableRowType]

    def __init__(
        self,
        row_type: Union[Type[PyAMTableRow], Dict[str, TypeEngine]],
        data_type=float,
    ) -> None:
        super().__init__()
        self.row_cls: Type = None
        self._db_model_cls: Type = None
        self.row_types: Dict[str, Column] = {}
        self.time_points: List[str] = []
        self.data_type: Union[Type[int], Type[float], Type[str]] = data_type
        if callable(row_type):
            self.row_cls = row_type
        elif isinstance(row_type, dict):
            self.row_cls = PyAMTableRow
            for prop_name, prop_value in row_type.items():
                self.row_types[prop_name] = Column(prop_value)
        else:
            raise NotImplementedError(
                f"Cannot recognize table row type {type(row_type)}"
            )

    def create_empty(self):
        return PyAMTable(PyAMTableRow)

    @staticmethod
    def parse_header(header_colnames_list: List[str]):
        """
        Parse the header row of an PyAM file.
        """
        keys: List[PyAMKey] = []
        time_points: List[str] = []
        for col_index, col_name in enumerate(header_colnames_list):
            # We assume that if the column name is decimal, it must be a timepoint.
            if col_name.isdecimal():
                time_points.append(col_name)
            else:
                assert col_name.isidentifier(), f"{col_name} should be an identifier"
                keys.append(PyAMKey(col_name, col_index))
        return keys, time_points

    def conv_type(self, item):
        if item == "" or item is None:
            return None
        return self.data_type(item)

    @staticmethod
    def from_file(
        file_name: str, row_types: RowType, data_type=float, encoding="utf-8"
    ):
        table = PyAMTable(
            row_types,
            data_type=data_type,
        )
        reader = TableReader(file_name, text_encoding=encoding)
        header, rows_iter = reader.read()
        columns, time_points = PyAMTable.parse_header(header)

        table.time_points = time_points
        for row_data in rows_iter:
            table_row_obj = table.row_cls(
                **{col.name: row_data[i] for i, col in enumerate(columns)}
            )
            table_row_obj.data = [
                table.conv_type(item) for item in row_data[len(columns) :]
            ]
            table.data.append(table_row_obj)
        return table

    @staticmethod
    def from_dicts(row_type: RowType, dicts: List[dict]):
        table = PyAMTable(row_type)
        for dic in dicts:
            table.data.append(table.row_cls(**dic))
        return table

    def find_one(self, query: Callable[[object], bool]) -> object:
        _, obj = self.find_one_with_index(query)
        return obj

    def find_one_with_index(
        self, query: Callable[[PyAMTableRowType], bool]
    ) -> Tuple[int, Optional[PyAMTableRowType]]:
        for i, obj in enumerate(self.data):
            if query(obj):
                return i, obj
        return -1, None

    def filter(
        self, query: Callable[[PyAMTableRowType], bool]
    ) -> "PyAMTable[PyAMTableRowType]":
        return cast(PyAMTable, super().filter(cast(Callable[[object], bool], query)))

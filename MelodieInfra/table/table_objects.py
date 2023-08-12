from typing import (
    Any,
    Callable,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    Dict,
    TypeVar,
)
from sqlalchemy import Column
from sqlalchemy.types import TypeEngine
from sqlalchemy.orm import declarative_base
from .reader_writer import TableReader, TableWriter, DatabaseConnector
from .table_base import TableBase, RowBase, py_types_to_sa_types, ColumnMeta

Base = declarative_base()

VEC_TEMPLATE = """
def vectorize_template(obj):
    return [{exprs}]
"""


class TableRow(RowBase):
    __table__: "Table"

    def __init__(self, table: "Table", **kwargs) -> None:
        self.__table__ = table
        if kwargs is not None:
            for k, v in kwargs.items():
                setattr(self, k, v)

    @classmethod
    def from_dict(cls, table: "Table", d: Dict, aliases: Dict[str, str]) -> "TableRow":
        r = TableRow(table)
        for k, v in d.items():
            setattr(r, aliases[k], v)
        return r

    @classmethod
    def get_annotations(cls) -> Dict[str, Union[Type[int], Type[str], Type[float]]]:
        return cls.__annotations__

    @classmethod
    def get_aliases(cls):
        attr_names = list(cls.__dict__.keys()) + list(cls.get_annotations().keys())
        aliases = {}
        for attr_name in attr_names:
            if hasattr(cls, attr_name) and isinstance(
                getattr(cls, attr_name), ColumnMeta
            ):
                attr: ColumnMeta = getattr(cls, attr_name)
                aliases[attr.column_name] = attr_name
            else:
                aliases[attr_name] = attr_name
        return aliases

    @classmethod
    def get_datatypes(cls):
        """
        Get the datatype represented in database.
        """
        attr_names = list(cls.__dict__.keys()) + list(cls.get_annotations().keys())
        attr_names = [
            attr_name
            for attr_name in list(set(attr_names))
            if not attr_name.startswith("__")
        ]
        dtypes = {}
        for attr_name in attr_names:
            assert (
                attr_name in cls.get_annotations()
            ), f'Attribute "{attr_name}" of class {cls.__name__} must be annotated!'
            if not hasattr(cls, attr_name):
                dtype = py_types_to_sa_types[cls.get_annotations()[attr_name]]()
            else:
                meta = getattr(cls, attr_name)
                assert isinstance(meta, ColumnMeta)
                if meta.dtype is not None:
                    dtype = meta.dtype
                else:
                    dtype = py_types_to_sa_types[cls.get_annotations()[attr_name]]()
            dtypes[attr_name] = dtype
        return dtypes

    @staticmethod
    def vectorizer(
        attrs: List[str],
    ) -> Callable[[object], List[Union[bool, int, float, str]]]:
        exprs = ",".join(["obj." + attr for attr in attrs])
        code = VEC_TEMPLATE.format(exprs=exprs)
        vars = {}
        exec(code, None, vars)
        return vars["vectorize_template"]

    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)

    def __getitem__(self, name):
        return getattr(self, name)


class TR(TableRow):
    pass


RowType = Union[Type, Dict[str, TypeEngine]]

TableRowGeneric = TypeVar("TableRowGeneric")


class Table(TableBase, Generic[TableRowGeneric]):
    data: List[TableRowGeneric]

    def __init__(self, row_type: Type[TableRowGeneric]) -> None:
        super().__init__()
        self.row_cls: Type[TableRow] = row_type
        self._db_model_cls: Type = None
        self.row_types: Dict[str, Column] = {}

        if callable(row_type) and issubclass(row_type, TableRow):
            self.row_types = row_type.get_datatypes()
        else:
            raise NotImplementedError(
                f"Cannot recognize table row type {type(row_type)}"
            )

    @property
    def columns(self):
        return [row for row in self.row_types.keys()]

    def clear(self):
        self.data = []

    def create_empty(self):
        return Table(self.row_cls)

    @staticmethod
    def parse_header(header_colnames_list: List[str]):
        """
        Parse the header row.
        """
        cols: List[str] = []
        for col_index, col_name in enumerate(header_colnames_list):
            cols.append(col_name)
            assert (
                col_name.isidentifier
            ), f"Column name '{col_name}' should be an identifier!"
        return cols

    @staticmethod
    def from_file(file_name: str, row_types: Type[TableRowGeneric], encoding="utf-8"):
        table = Table(row_type=row_types)
        reader = TableReader(file_name, text_encoding=encoding)
        header, rows_iter = reader.read()
        columns = Table.parse_header(header)
        aliases = table.row_cls.get_aliases()
        for row_data in rows_iter:
            table_row_obj: TableRow = table.row_cls.from_dict(
                table, {col: row_data[i] for i, col in enumerate(columns)}, aliases
            )
            table.data.append(table_row_obj)
        return table

    def to_file(self, file_name: str, encoding="utf-8"):
        writer = TableWriter(file_name, text_encoding=encoding).write()
        headers = self.columns
        writer.send(headers)
        for row_data in self.data:
            writer.send([row_data.__dict__[k] for k in headers])
        writer.close()

    def to_database(self, engine, table_name: str):
        conn = DatabaseConnector(engine)
        conn.write_table(table_name, self.row_types, [d.__dict__ for d in self.data])

    def to_file_with_codegen(self, file_name: str, encoding="utf-8"):
        writer = TableWriter(file_name, text_encoding=encoding).write()
        headers = [row for row in self.row_types.keys()]
        writer.send(headers)
        vectorizer = TableRow.vectorizer(headers)
        for row_data in self.data:
            writer.send(vectorizer(row_data))
        writer.close()

    @staticmethod
    def from_dicts(row_type: RowType, dicts: List[dict]):
        table = Table(row_type)
        aliases = table.row_cls.get_aliases()
        print(aliases)
        for dic in dicts:
            table.data.append(table.row_cls.from_dict(table, dic, aliases))
        return table

    def apply(self, ufunc: Callable[[TableRowGeneric], None]) -> None:
        for row in self.data:
            ufunc(row)

    def find_one(
        self, query: Callable[[TableRowGeneric], bool]
    ) -> Optional[TableRowGeneric]:
        _, obj = self.find_one_with_index(query)
        return obj

    def find_one_with_index(
        self, query: Callable[[TableRowGeneric], bool]
    ) -> Tuple[int, Optional[TableRowGeneric]]:
        for i, obj in enumerate(self.data):
            if query(obj):
                return i, obj
        return -1, None

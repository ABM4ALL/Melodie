from dataclasses import dataclass
from sqlalchemy.types import BigInteger, Text, TypeEngine, Float, Boolean
from typing import Callable, Dict, List, Optional, Tuple, TypeVar, Type, Any

py_types_to_sa_types: Dict[Type, Type[TypeEngine]] = {
    int: BigInteger,
    str: Text,
    float: Float,
    bool: Boolean,
}


@dataclass
class ColumnMeta:
    column_name: str
    dtype: Optional[TypeEngine]

    def __post_init__(self):
        assert isinstance(self.dtype, TypeEngine) or self.dtype is None, self.dtype


def column_meta(col_name: str, dtype: Optional[TypeEngine] = None) -> Any:
    o = ColumnMeta(col_name, dtype)
    return o


class RowBase:
    def payload_to_str(self):
        return f"{self.__dict__}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.payload_to_str()}>"


class TableBase:
    class IatObjectsIndicer:
        def __init__(self, data: List) -> None:
            self.data = data

        def __getitem__(self, indices):
            return getattr(self.data[indices[0]], indices[1])

    class IatDictsIndicer:
        def __init__(self, data: List) -> None:
            self.data = data

        def __getitem__(self, indices):
            return self.data[indices[0]][indices[1]]

    def __init__(self) -> None:
        self.data: List[object] = []

    def __len__(self):
        return len(self.data)

    @property
    def columns(self):
        raise NotImplementedError

    def create_empty(self):
        raise NotImplementedError("Abstract method")

    def create_same_schemed_empty(self):
        new_table: TableBase = self.create_empty()
        for k, v in new_table.__dict__.items():
            if k != "data":
                setattr(new_table, k, v)
        new_table.data = []
        return new_table

    def find_one_with_index(
        self, query: Callable[[object], bool]
    ) -> Tuple[int, object]:
        for i, obj in enumerate(self.data):
            if query(obj):
                return i, obj
        return -1, None

    def find_all_with_index(
        self, query: Callable[[object], bool]
    ) -> List[Tuple[int, object]]:
        result = []
        for i, obj in enumerate(self.data):
            if query(obj):
                result.append((i, obj))
        return result

    def find_all(self, query: Callable[[object], bool]) -> List[object]:
        result = []
        for obj in self.data:
            if query(obj):
                result.append(obj)
        return result

    def filter(self, query: Callable[[object], bool]):
        new_data = self.find_all(query)
        new_table = self.create_same_schemed_empty()
        new_table.data = new_data
        return new_table

    @property
    def iat(self):
        return TableBase.IatObjectsIndicer(self.data)

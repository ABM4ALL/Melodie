"""
Compatibility layer for internal table types and pandas data frame.
"""
from typing import Callable, List, Union, TYPE_CHECKING, Iterator
from .table_base import TableBase

import pandas as pd

TABLE_TYPE = Union["pd.DataFrame", TableBase]


class TableInterface:
    def __init__(self, df: TABLE_TYPE) -> None:
        self.df = df

    def __len__(self):
        return len(self.df)

    @property
    def columns(self) -> List[str]:
        return self.df.columns

    def filter(self, condition: Callable) -> "TableInterface":
        """
        Filter records in df according to condition
        """
        if isinstance(self.df, TableBase):
            return TableInterface(self.df.filter(condition))
        else:
            if not isinstance(self.df, pd.DataFrame):
                raise TypeError(self.df)
            return TableInterface(self.df[self.df.apply(condition, axis=1)])

    def iter_dicts(self) -> Iterator[dict]:
        """
        Row iteration interface for both internal table types or pandas table types
        """
        if isinstance(self.df, TableBase):
            for row in self.df.data:
                yield row
        else:
            if not isinstance(self.df, pd.DataFrame):
                raise TypeError(self.df)
            df_dict = self.df.to_dict(orient="records")
            for item in df_dict:
                yield item

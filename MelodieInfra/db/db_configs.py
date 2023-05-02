import abc
from typing import Union


class BaseMelodieDBConfig(abc.ABC):
    def __init__(self):
        self.type = ""

    @abc.abstractmethod
    def connection_string(self) -> str:
        pass


class SQLiteDBConfig(BaseMelodieDBConfig):
    def __init__(self, db_file: str = ""):
        super().__init__()
        self.type = 'sqlite'
        self.db_file = db_file

    def connection_string(self) -> str:
        return f"sqlite:///{self.db_file}"


class MysqlDBConfig(BaseMelodieDBConfig):
    def __init__(self, db_name: str, host: str, user: str, password: str):
        super().__init__()
        self.type == "mysql"
        self.db_name = db_name
        self.host = host
        self.user = user
        self.password = password

    def connection_string(self) -> str:
        return f"mysql+pymysql://{self.user}:{self.password}@{self.host}/{self.db_name}?charset=utf8mb4"


DBConfigTypes = Union[MysqlDBConfig, SQLiteDBConfig]

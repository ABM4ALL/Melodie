import abc
from typing import Dict, Union


class BaseMelodieDBConfig(abc.ABC):
    def __init__(self):
        self.type = ""

    @abc.abstractmethod
    def connection_string(self) -> str:
        pass

    def to_json(self):
        return self.__dict__

    @staticmethod
    def from_json(config_json: Dict[str, str]):
        types = {"sqlite": SQLiteDBConfig, "mysql": MysqlDBConfig}
        config_type = config_json.pop("type")
        return types[config_type](**config_json)


class SQLiteDBConfig(BaseMelodieDBConfig):
    def __init__(self, db_file: str = ""):
        super().__init__()
        self.type = "sqlite"
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

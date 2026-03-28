import os

from Melodie import Config
from MelodieInfra.db.db_configs import MysqlDBConfig


def test_config_from_dict_roundtrip():
    cfg = Config(
        "demo",
        os.path.dirname(__file__),
        input_folder=os.path.join(os.path.dirname(__file__), "resources"),
        output_folder=os.path.join(os.path.dirname(__file__), "resources", "temp"),
        visualizer_entry="",
        data_output_type="sqlite",
        database_config=MysqlDBConfig("demo", "localhost", "user", "pw"),
        input_cache=True,
        studio_port=9001,
        visualizer_port=9002,
        parallel_port=9003,
    )

    restored = Config.from_dict(cfg.to_dict())

    assert restored.data_output_type == "sqlite"
    assert restored.input_dataframe_cache is True
    assert restored.studio_port == 9001
    assert restored.visualizer_port == 9002
    assert restored.parallel_port == 9003
    assert restored.database_config.type == "mysql"

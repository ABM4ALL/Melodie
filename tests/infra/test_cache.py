import os

import pandas as pd

from MelodieInfra.utils import PickledCacheFileReader
from tests.infra.config import resources_path


def test_file_reader():
    FILE = os.path.join(resources_path, "excels", "only_scenarios_right.xlsx")
    reader = PickledCacheFileReader(
        os.path.join(resources_path, "cache", "tables"),
        lambda filename: pd.read_excel(filename),
    )
    df_original = reader.read(FILE)
    df_from_cache = reader.read(FILE)

    assert df_original.shape == df_from_cache.shape

from typing import Dict, Type, Union

TABLE_DTYPES = Dict[
    str,
    Union[
        str, Type[str], Type[float], Type[int], Type[complex], Type[bool], Type[object]
    ],
]

SQLITE_FILE_SUFFIX = ".sqlite"

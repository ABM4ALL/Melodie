import abc
import hashlib
import os
from typing import Callable, Generic, TypeVar

import cloudpickle
import pandas as pd

CachedDataType = TypeVar("CachedDataType")


def calc_hash(filename: str) -> str:
    """
    Calculate hash of file identified by `filename`.
    """
    with open(filename, "rb") as fp:
        data = fp.read()
    file_md5 = hashlib.md5(data).hexdigest()
    return file_md5


class CacheFileReader(abc.ABC, Generic[CachedDataType]):
    def __init__(self, cache_dir: str) -> None:
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        assert self.cache_file_ext.startswith(".")

    @property
    @abc.abstractmethod
    def cache_file_ext(self) -> str:
        """
        Get the extension name of the cache file
        """

    @abc.abstractmethod
    def read_original_file(self, filename: str) -> CachedDataType:
        """
        Read from the original data file, must return a valid data kind
        """

    @abc.abstractmethod
    def write_cache(self, cache_file: str, data: CachedDataType):
        """
        write data to cache file.
        """

    @abc.abstractmethod
    def read_cache(self, cache_file: str) -> CachedDataType:
        pass

    def read(self, filename: str) -> CachedDataType:
        """
        Read file.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(filename)
        hash_value = calc_hash(filename)

        cache_file = os.path.join(self.cache_dir, hash_value + self.cache_file_ext)
        if os.path.exists(cache_file):
            return self.read_cache(cache_file)
        else:
            data = self.read_original_file(filename)
            self.write_cache(cache_file, data)
            return data


class PickledCacheFileReader(CacheFileReader[CachedDataType]):
    def __init__(
        self, cache_dir: str, original_read_method: Callable[[str], CachedDataType]
    ) -> None:
        super().__init__(cache_dir)
        self.original_read_method = original_read_method

    @property
    def cache_file_ext(self):
        return ".pkl"

    def read_cache(self, cache_file: str) -> CachedDataType:
        with open(cache_file, "rb") as f:
            return cloudpickle.load(f)

    def write_cache(self, cache_file: str, data: CachedDataType) -> None:
        with open(cache_file, "wb") as f:
            cloudpickle.dump(data, f)

    def read_original_file(self, filename: str) -> CachedDataType:
        return self.original_read_method(filename)

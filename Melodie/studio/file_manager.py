import json
import os
from typing import ClassVar, Dict, Any, List, Optional, Tuple, Type, Union


class JSONManager():

    @staticmethod
    def from_file(file_name: str, allowed_types: Type['JSONManager']) -> Tuple[
            Optional[Union[List[Any], Dict[str, Any]]],
            Union[str, None]]:
        if not os.path.exists(file_name):
            return None, f"File '{file_name}' does not exist!"
        try:
            with open(file_name, encoding="utf8") as f:
                content: Union[List[Any], Dict[str, Any]] = json.load(f)
            if isinstance(content, allowed_types):
                return content, None
            else:
                return None, f"Content is not of allowed types!"

        except json.JSONDecodeError:
            return None, f"Decode error occured for file '{file_name}'"

    @staticmethod
    def to_file(obj: Union[Dict[str, Any], List[Any]], file_name: str) -> Union[str, None]:
        try:
            with open(file_name, "w", encoding="utf8") as f:
                json.dump(obj, f)
            return None
        except OSError as e:
            return f"{e}"


class ChartsConfigManager():
    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    JSONManager()

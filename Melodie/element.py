import logging
import warnings
from typing import Any, Dict


class Element:
    def set_params(self, params: Dict[str, Any], asserts_key_exist=True):
        """
        Set parameters for this element from a dictionary.

        This method iterates through a dictionary of parameters and assigns them
        as attributes to the object.

        :param params: A dictionary where keys are attribute names and values are
            the corresponding values to be set.
        :param asserts_key_exist: If ``True`` (default), an error will be raised
            if a key from the ``params`` dictionary does not correspond to an
            existing attribute of the object.
        """
        for paramName, paramValue in params.items():
            msg = f"Parameter '{paramName}' with value '{paramValue}' does not exist in the attributes of {self.__class__.__name__}."
            if paramName not in self.__dict__.keys():
                if asserts_key_exist:
                    raise AttributeError(msg)

            setattr(self, paramName, paramValue)

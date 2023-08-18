from typing import List, Callable, Union, Type
from .table_objects import Table

DATA_TYPES = Union[bool, int, float, str]

VEC_TEMPLATE = """
def vectorize_template(table, obj):
    return {class_name}(table, {exprs})
"""


def objs_to_table_row_vectorizer(
    cls: Type,
    attrs: List[str],
) -> Callable[[Table, object], object]:
    exprs = ",".join([f"{attr}=obj.{attr}" for attr in attrs])
    code = VEC_TEMPLATE.format(class_name=cls.__name__, exprs=exprs)
    vars = {}
    globals()[cls.__name__] = cls
    exec(code, None, vars)
    return vars["vectorize_template"]

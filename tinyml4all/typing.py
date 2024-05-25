from pathlib import Path
from typing import List, Union, Any, Type, Callable

ListOfStrings = Union[str, List[str]]
Filename = Union[str, Path]


def as_list_of_strings(l: ListOfStrings) -> List[str]:
    """
    Convert comma-separated string into a list
    :param l:
    :return:
    """
    if isinstance(l, str):
        return [s.strip() for s in l.split(",") if s.strip()]

    return l


def cast(x: Any, dtype: Type, caster: Callable = None) -> Any:
    """
    Cast variable to given type, if not already
    :param x: variable to convert
    :param dtype: desired type
    :param caster: custom caster, if dtype is not a constructor
    :return:
    """
    if isinstance(x, dtype):
        return x

    return dtype(x) if caster is None else caster(x)

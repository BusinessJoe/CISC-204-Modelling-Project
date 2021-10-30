"""This module implements useful logic operations"""
import operator
from functools import reduce
from typing import Any
from nnf import Var


def _is_iterable(arg: Any) -> bool:
    """Returns True if arg is iterable and false otherwise"""
    try:
        iter(arg)
        return True
    except TypeError:
        return False


def _expand_iterable(func):
    """Decorator that expands the first argument if it is the only argument and iterable

    This makes func([1, 2, 3]) the same as func(1, 2, 3)
    """

    def wrapper(*args):
        if len(args) == 1 and _is_iterable(args[0]):
            return func(*(args[0]))
        return func(*args)

    return wrapper


def implication(left: Var, right: Var) -> Var:
    """Returns a Var equal to (left implies right)"""
    return left.negate() | right


@_expand_iterable
def multi_or(*args: Var) -> Var:
    return reduce(operator.__or__, args)


@_expand_iterable
def multi_and(*args: Var) -> Var:
    return reduce(operator.__and__, args)


@_expand_iterable
def one_of(*args: Var) -> Var:
    parts = []
    for idx in range(len(args)):
        parts.append(
            multi_and(*(a if i == idx else a.negate() for i, a in enumerate(args)))
        )
    return multi_or(*parts)


@_expand_iterable
def none_of(*args: Var) -> Var:
    return multi_and(*(a.negate() for a in args))


@_expand_iterable
def one_of_or_none(*args: Var) -> Var:
    return one_of(*args) | multi_and(*(a.negate() for a in args))

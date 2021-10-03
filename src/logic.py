"""This module implements useful logic operations"""
import operator
from functools import reduce
from nnf import Var


def implication(left: Var, right: Var) -> Var:
    return left.negate() | right


def multi_or(*args: Var) -> Var:
    return reduce(operator.__or__, args)


def multi_and(*args: Var) -> Var:
    return reduce(operator.__and__, args)


def one_of(*args: Var) -> Var:
    parts = []
    for idx in range(len(args)):
        parts.append(
            multi_and(*(a if i == idx else a.negate() for i, a in enumerate(args)))
        )
    return multi_or(*parts)


def none_of(*args: Var) -> Var:
    return multi_and(*(a.negate() for a in args))


def one_of_or_none(*args: Var) -> Var:
    return one_of(*args) | multi_and(*(a.negate() for a in args))

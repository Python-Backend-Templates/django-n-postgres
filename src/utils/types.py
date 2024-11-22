from dataclasses import Field
from types import UnionType
from typing import TypeVar, Union, get_args, get_origin

from rest_framework.serializers import empty

TValue = TypeVar("TValue")


def is_optional(field: Field) -> bool:
    return get_origin(field.type) in (Union, UnionType) and type(None) in get_args(
        field.type
    )


def resolve_value(old: TValue, new: empty | TValue | None) -> TValue:
    if new is empty or new is None:
        return old
    return new


def resolve_nullable_value(
    old: TValue,
    new: empty | TValue,
    *,
    value_nullable: bool = True,
) -> TValue:
    if new is empty or (not value_nullable and new is None):
        return old
    return new

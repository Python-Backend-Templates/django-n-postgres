"""
Implementations here are experimental,
and might not work with complex schemas.
Consider using Pydantic for more robust convertation/validation.
"""

from dataclasses import MISSING, Field, fields, is_dataclass
from types import UnionType
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
)

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from utils.interfaces import IConvertDict

if TYPE_CHECKING:
    TDataclass = TypeVar("TDataclass", bound=DataclassInstance)
else:
    TDataclass = TypeVar("TDataclass")


class ConvertDictToDataclass(IConvertDict[TDataclass]):
    def __init__(self, target_class: Type[TDataclass]) -> None:
        """
        ### Args:
            target_class: dataclass type to convert to.
                Supported types and behaviour:
                    - Built in type (primitives, iterable of primitives,
                            mapping of primitives) are passed to dataclass as is
                    - Dataclass is recursevily converted
                    - List or Tuple of dataclass type is recursevily converted
                    - Missing values in `obj` will raise `ValueError`,
                        unless specified type in dataclass is `Optional` or
                        has a default value
        """
        self.target_class = target_class
        self.is_empty = len(fields(self.target_class)) == 0

    def __call__(self, obj: Dict[str, Any] | None) -> TDataclass:
        """
        ### Args:
            obj: dictionary to convert

        ### Returns:
            Dataclass instance constructed from `obj`

        ### Raises
            ValueError - if passed object can't be converted to target dataclass
        """
        if not obj:
            if self.is_empty:
                # we can initiate our target class without params,
                # because we are sure it has no fields
                return self.target_class()
            raise ValueError("Received an empty message for non-empty dataclass.")

        return self._convert(
            obj,
            self.target_class,
        )

    def _convert(self, obj: Dict[str, Any], dataclass: Type[TDataclass]) -> TDataclass:
        result: Dict[str, Any] = dict()
        for field in fields(dataclass):
            if field.name not in obj.keys():
                result[field.name] = self._resolve_missing(field)
                continue

            if self._list_or_tuple_of_dataclass(field):
                result[field.name] = list(
                    self._convert(item, field.type.__args__[0])
                    for item in obj[field.name]
                )
                continue

            if is_dataclass(field.type):
                result[field.name] = self._convert(
                    obj[field.name],
                    field.type,  # type:ignore[arg-type]
                )
                continue

            # attribute with primitive type
            result[field.name] = obj[field.name]

        return dataclass(**result)

    def _resolve_missing(self, field: Field) -> Any | None:
        if self._is_optional(field):
            return None
        if self._has_default(field):
            return field.default

        raise ValueError(
            f"Invalid object for class - {self.target_class.__class__.__name__}"
        )

    def _is_optional(self, field: Field) -> bool:
        return get_origin(field.type) in (Union, UnionType) and type(None) in get_args(
            field.type
        )

    def _has_default(self, field: Field) -> bool:
        return field.default is not MISSING

    def _list_or_tuple_of_dataclass(self, field: Field) -> bool:
        return (
            hasattr(field.type, "__origin__")
            and field.type.__origin__ in (list, tuple)
            and hasattr(field.type, "__args__")
            and field.type.__args__
            and is_dataclass(field.type.__args__[0])
        )


class ConvertNestedDictToDict(IConvertDict[Dict[str, Any]]):
    def __call__(self, obj: Dict[str, Any] | None) -> Dict:
        if not obj:
            return dict()

        return self._resolve_mapping(namespace="", value=obj)

    def _resolve_mapping(self, namespace: str, value: Dict) -> Dict:
        if not value:
            return {namespace: value}
        result: Dict[str, Any] = dict()
        for k, v in value.items():
            if self._is_mapping(v):
                result = {
                    **result,
                    **self._resolve_mapping(f"{namespace}_{k}" if namespace else k, v),
                }
                continue
            nk, nv = self._resolve_primitive(namespace, k, v)
            result[nk] = nv

        return result

    def _is_mapping(self, value: Any) -> bool:
        return isinstance(value, dict)

    def _resolve_primitive(
        self, namespace: str, key: str, value: Any
    ) -> Tuple[str, str]:
        if value is None:
            return (f"{namespace}_{key}", "null") if namespace else (key, "null")

        try:
            val = str(value)
        except (ValueError, TypeError):
            return (f"{namespace}_{key}", "null") if namespace else (key, "null")
        else:
            return (f"{namespace}_{key}", val) if namespace else (key, val)

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, Iterable, List, Sequence, Type, TypeVar

from django.db.models import Model, QuerySet
from django.shortcuts import get_object_or_404

T = TypeVar("T", bound=Model)


class IRepo(ABC, Generic[T]):
    @abstractmethod
    def all(self) -> QuerySet[T]: ...

    @abstractmethod
    def get_by_id(self, id_: int, *, for_update: bool = False) -> T: ...

    @abstractmethod
    def get_by_ids(
        self, ids: List[int], *, for_update: bool = False
    ) -> QuerySet[T]: ...

    @abstractmethod
    def get_by_field(
        self, field: str, value: Any, *, for_update: bool = False
    ) -> T: ...

    @abstractmethod
    def update(self, instance: T) -> None: ...

    @abstractmethod
    def multi_update(self, ids: List[int], *, values: Dict[str, Any]) -> None: ...

    @abstractmethod
    def bulk_update(self, instances: Iterable[T], *, fields: Sequence[str]) -> None: ...

    @abstractmethod
    def delete(self, instance: T) -> None: ...

    @abstractmethod
    def delete_by_field(self, field: str, value: Any) -> None: ...


class Repo(IRepo[T]):
    def __init__(self, model_class: Type[T]) -> None:
        self.model_class = model_class

    def all(self) -> QuerySet[T]:
        return self.model_class.objects.all()  # type: ignore

    def get_by_id(self, id_: int, *, for_update: bool = False) -> T:
        qs = self.model_class.objects  # type: ignore
        if for_update:
            qs = qs.select_for_update()
        return get_object_or_404(qs, pk=id_)

    def get_by_ids(self, ids: List[int], *, for_update: bool = False) -> QuerySet[T]:
        qs = self.model_class.objects  # type: ignore
        if for_update:
            qs = qs.select_for_update()
        return qs.filter(pk__in=ids)

    def get_by_field(self, field: str, value: Any, *, for_update: bool = False) -> T:
        qs = self.model_class.objects  # type: ignore
        if for_update:
            qs = qs.select_for_update()
        return qs.filter(**{field: value})

    def update(self, instance: T) -> None:
        instance.save()

    def multi_update(self, ids: List[int], *, values: Dict[str, Any]) -> None:
        self.get_by_ids(ids).update(**values)

    def bulk_update(self, instances: Iterable[T], *, fields: Sequence[str]) -> None:
        self.model_class.objects.bulk_update(instances, fields=fields)  # type: ignore

    def delete(self, instance: T) -> None:
        instance.delete()

    def delete_by_field(self, field: str, value: Any) -> None:
        self.model_class.objects.filter(**{field: value}).delete()  # type: ignore

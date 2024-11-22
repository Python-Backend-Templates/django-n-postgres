from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    List,
    Sequence,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
)

from django.db.models import Aggregate, Model, QuerySet
from django.shortcuts import get_object_or_404

from utils.cache import cache

T = TypeVar("T", bound=Model)

FieldToAggregate: TypeAlias = Dict[str, Aggregate]
FieldToAggregateResult: TypeAlias = Dict[str, Any]
Filters: TypeAlias = Dict[str, Any]


class IRepo(ABC, Generic[T]):
    model_class: Type[T]
    is_soft_deletable: bool

    @abstractmethod
    def all(
        self,
        *,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]: ...
    @abstractmethod
    def get_by_id(
        self, id_: int, *, for_update: bool = False, include_soft_deleted: bool = False
    ) -> T: ...
    @abstractmethod
    def get_by_ids(
        self,
        ids: List[int],
        *,
        for_update: bool = False,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]: ...
    @abstractmethod
    def get_by_field(
        self,
        field: str,
        value: Any,
        *,
        for_update: bool = False,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]: ...
    @abstractmethod
    def get_by_filters(
        self,
        *,
        filters: Filters,
        for_update: bool = False,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]: ...
    @abstractmethod
    def get_first_by_field(
        self,
        field: str,
        value: Any,
        *,
        for_update: bool = False,
        include_soft_deleted: bool = False,
    ) -> T | None: ...
    @abstractmethod
    def get_first_by_filters(
        self,
        *,
        filters: Filters,
        for_update: bool = False,
        include_soft_deleted: bool = False,
    ) -> T | None: ...
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
    @abstractmethod
    def exists_by_field(
        self, field: str, value: Any, *, include_soft_deleted: bool = False
    ) -> bool: ...
    @abstractmethod
    def aggregate(
        self,
        *,
        aggregates: Dict[str, Aggregate],
        filters: Filters | None = None,
        include_soft_deleted: bool = False,
    ) -> FieldToAggregateResult: ...
    @abstractmethod
    def count_by_filters(
        self,
        *,
        filters: Filters,
        qs: QuerySet[T] | None = None,
        include_soft_deleted: bool = False,
    ) -> int: ...
    @abstractmethod
    def exists_by_filters(
        self,
        *,
        filters: Filters,
        qs: QuerySet[T] | None = None,
        include_soft_deleted: bool = False,
    ) -> bool: ...


class Repo(IRepo[T]):
    def __init__(self, model_class: Type[T], is_soft_deletable: bool = False) -> None:
        self.model_class = model_class
        self.is_soft_deletable = is_soft_deletable

    @cache(result_type="queryset")
    def all(
        self,
        *,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]:
        return self._resolve_qs_options(
            qs=self.model_class.objects.all(),  # type: ignore[attr-defined]
            include_soft_deleted=include_soft_deleted,
            ordering=ordering,
            select_related=select_related,
        )

    @cache(result_type="instance")
    def get_by_id(
        self,
        id_: int,
        *,
        for_update: bool = False,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> T:
        qs = self.model_class.objects  # type: ignore[attr-defined]
        if for_update:
            qs = qs.select_for_update()
        return get_object_or_404(
            self._resolve_qs_options(
                qs=qs,
                include_soft_deleted=include_soft_deleted,
                ordering=ordering,
                select_related=select_related,
            ),
            pk=id_,
        )

    def get_by_ids(
        self,
        ids: List[int],
        *,
        for_update: bool = False,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]:
        qs = self.model_class.objects  # type: ignore[attr-defined]
        if for_update:
            qs = qs.select_for_update()
        return self._resolve_qs_options(
            qs=qs.filter(pk__in=ids),
            include_soft_deleted=include_soft_deleted,
            ordering=ordering,
            select_related=select_related,
        )

    def get_by_field(
        self,
        field: str,
        value: Any,
        *,
        for_update: bool = False,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]:
        qs = self.model_class.objects  # type: ignore[attr-defined]
        if for_update:
            qs = qs.select_for_update()
        return self._resolve_qs_options(
            qs=qs.filter(**{field: value}),
            include_soft_deleted=include_soft_deleted,
            ordering=ordering,
            select_related=select_related,
        )

    def get_by_filters(
        self,
        *,
        filters: Filters,
        for_update: bool = False,
        include_soft_deleted: bool = False,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]:
        qs = self.model_class.objects  # type: ignore[attr-defined]
        if for_update:
            qs = qs.select_for_update()
        return self._resolve_qs_options(
            qs=qs.filter(**filters),
            include_soft_deleted=include_soft_deleted,
            ordering=ordering,
            select_related=select_related,
        )

    def get_first_by_field(
        self,
        field: str,
        value: Any,
        *,
        for_update: bool = False,
        include_soft_deleted: bool = False,
    ) -> T | None:
        return self.get_by_field(
            field,
            value,
            for_update=for_update,
            include_soft_deleted=include_soft_deleted,
        ).first()

    def get_first_by_filters(
        self,
        *,
        filters: Filters,
        for_update: bool = False,
        include_soft_deleted: bool = False,
    ) -> T | None:
        return self.get_by_filters(
            filters=filters,
            for_update=for_update,
            include_soft_deleted=include_soft_deleted,
        ).first()

    def update(self, instance: T) -> None:
        instance.save()

    def multi_update(self, ids: List[int], *, values: Dict[str, Any]) -> None:
        self.get_by_ids(ids).update(**values)

    def bulk_update(self, instances: Iterable[T], *, fields: Sequence[str]) -> None:
        self.model_class.objects.bulk_update(  # type: ignore[attr-defined]
            instances, fields=fields
        )

    def delete(self, instance: T) -> None:
        if self.is_soft_deletable:
            # soft deletion must be done with updating `is_deleted` field
            return
        instance.delete()

    def delete_by_field(self, field: str, value: Any) -> None:
        if self.is_soft_deletable:
            # soft deletion must be done with updating `is_deleted` field
            return

        self.model_class.objects.filter(  # type: ignore[attr-defined]
            **{field: value}
        ).delete()

    def exists_by_field(
        self, field: str, value: Any, *, include_soft_deleted: bool = False
    ) -> bool:
        return self._resolve_qs_options(
            qs=self.model_class.objects.filter(  # type: ignore[attr-defined]
                **{field: value}
            ),
            include_soft_deleted=include_soft_deleted,
        ).exists()

    def aggregate(
        self,
        *,
        aggregates: FieldToAggregate,
        filters: Filters | None = None,
        include_soft_deleted: bool = False,
    ) -> FieldToAggregateResult:
        filters = filters or {}
        return self.get_by_filters(
            filters=filters,
            for_update=False,
            include_soft_deleted=include_soft_deleted,
        ).aggregate(**aggregates)

    def count_by_filters(
        self,
        *,
        filters: Filters,
        qs: QuerySet[T] | None = None,
        include_soft_deleted: bool = False,
    ) -> int:
        if qs is None:
            qs = self.model_class.objects  # type: ignore[attr-defined]
        return self._resolve_qs_options(
            qs=qs.filter(**filters),
            include_soft_deleted=include_soft_deleted,
        ).count()

    def exists_by_filters(
        self,
        *,
        filters: Filters,
        qs: QuerySet[T] | None = None,
        include_soft_deleted: bool = False,
    ) -> bool:
        if qs is None:
            qs = self.model_class.objects  # type: ignore[attr-defined]
        return self._resolve_qs_options(
            qs=qs.filter(**filters),
            include_soft_deleted=include_soft_deleted,
        ).exists()

    """ protected """

    def _fetch_queries(
        self,
        queryset: QuerySet[T],
        select_related_fields: tuple[str, ...] | None = None,
    ) -> QuerySet[T]:
        if select_related_fields:
            return queryset.select_related(*select_related_fields)
        return queryset

    def _resolve_qs_options(
        self,
        *,
        qs: QuerySet[T],
        include_soft_deleted: bool,
        ordering: Tuple[str] | None = None,
        select_related: Tuple[str] | None = None,
    ) -> QuerySet[T]:
        if self.is_soft_deletable and not include_soft_deleted:
            qs = qs.filter(is_deleted=False)
        if ordering:
            qs = qs.order_by(*ordering)
        if select_related:
            qs = qs.select_related(*select_related)
        return qs

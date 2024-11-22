from typing import Any

from rest_framework import status, serializers
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.request import Request


class CustomCreateModelMixin(CreateModelMixin):
    """
    Create a model instance.
    """

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_serializer = self.perform_create(serializer)
        serializer = new_serializer if new_serializer else serializer
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer: serializers.Serializer) -> Any:
        return serializer.save()


class CustomUpdateModelMixin(UpdateModelMixin):
    """
    Update a model instance
    """

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_serializer = self.perform_update(serializer)
        serializer = new_serializer if new_serializer else serializer

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers, status


class BaseMessageSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)


class MessageErrorSerializer(serializers.Serializer):
    detail = serializers.CharField(required=False)
    field_name = serializers.ListField(child=serializers.CharField(), required=False)


class Unauthorized401Serializer(serializers.Serializer):
    detail = serializers.CharField()
    code = serializers.CharField()
    messages = MessageErrorSerializer(many=True)


class NotFound404Serializer(serializers.Serializer):
    detail = serializers.CharField()


class Forbidden403Serializer(serializers.Serializer):
    detail = serializers.CharField()


class PaginationParametersSerializer(serializers.Serializer):
    page_size = serializers.IntegerField(required=False)
    page = serializers.IntegerField(required=False)


def get_paginated_schema(serializer_class):
    return {
        status.HTTP_200_OK: inline_serializer(
            name="DefaultPaginationSchema",
            fields=__get_default_pagination_fields(serializer_class),
        )
    }


def __get_default_pagination_fields(serializer_class):
    return {
        "total": serializers.IntegerField(default=123),
        "pages": serializers.IntegerField(default=1),
        "is_last": serializers.BooleanField(default=False),
        "results": serializer_class(many=True),
    }

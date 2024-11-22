from typing import Any, Dict, Optional, Sequence, Type, Union

from django.utils.translation import gettext_lazy as _
from django.utils.functional import Promise
from drf_spectacular.utils import OpenApiCallback, OpenApiExample, OpenApiParameter
from drf_spectacular.utils import extend_schema as _extend_schema
from rest_framework import status
from rest_framework.fields import empty
from rest_framework.serializers import Serializer

from utils import openapi, serializers

_SerializerType = Union[Serializer, Type[Serializer]]
_StrOrPromise = Union[str, Promise]
_SchemaType = Dict[str, Any]


NotFoundObjectExample = OpenApiExample(
    _("Объект не найден"),
    value={"detail": "Страница не найдена."},
    response_only=True,
    status_codes=[404],
)

ForbiddenExample = OpenApiExample(
    _("Недостаточно прав"),
    value={"detail": "У вас недостаточно прав для выполнения данного действия."},
    response_only=True,
    status_codes=[403],
)

UnauthorizedExample = OpenApiExample(
    _("Токен недействителен"),
    value={
        "detail": "Данный токен недействителен для любого типа токена",
        "code": "token_not_valid",
        "messages": [
            {
                "token_class": "AccessToken",
                "token_type": "access",
                "message": "Токен недействителен или просрочен",
            }
        ],
    },
    response_only=True,
    status_codes=[401],
)

UnauthorizedNonTokenExample = OpenApiExample(
    _("Токен не был представлен"),
    value={"detail": "Учетные данные не были предоставлены."},
    response_only=True,
    status_codes=[401],
)


TooManyRequestsExample = OpenApiExample(
    _("Слишком много запросов"),
    value={
        "detail": "Запрос был проигнорирован. Ожидается доступность через 60 секунд."
    },
    response_only=True,
    status_codes=[429],
)


InternalErrorExample = OpenApiExample(
    _("Внутренняя ошибка"),
    value={"detail": _("Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.")},
    response_only=True,
    status_codes=[500],
)


def extend_schema(
    operation_id: Optional[str] = None,
    parameters: Optional[Sequence[Union[OpenApiParameter, _SerializerType]]] = None,
    request: Any = empty,
    responses: Dict = empty,
    auth: Optional[Sequence[str]] = None,
    description: Optional[_StrOrPromise] = None,
    summary: Optional[_StrOrPromise] = None,
    deprecated: Optional[bool] = None,
    tags: Optional[Sequence[str]] = None,
    filters: Optional[bool] = None,
    exclude: Optional[bool] = None,
    operation: Optional[_SchemaType] = None,
    methods: Optional[Sequence[str]] = None,
    versions: Optional[Sequence[str]] = None,
    examples: Optional[Sequence[OpenApiExample]] = None,
    extensions: Optional[Dict[str, Any]] = None,
    callbacks: Optional[Sequence[OpenApiCallback]] = None,
    external_docs: Optional[Union[Dict[str, str], str]] = None,
):
    """Overriden `extend_schema` decorator with included default responses and examples"""
    if not responses or responses is empty:
        responses = {}
    responses.setdefault(
        status.HTTP_429_TOO_MANY_REQUESTS, serializers.TooManyRequests429Serializer
    )
    responses.setdefault(
        status.HTTP_500_INTERNAL_SERVER_ERROR, serializers.internal_error_serializer
    )

    if not examples:
        examples = []
    examples.extend(
        (
            openapi.TooManyRequestsExample,
            openapi.InternalErrorExample,
        )
    )

    if not parameters:
        parameters = []
    parameters.extend(
        (
            OpenApiParameter(
                name="X-Request-Id",
                type=str,
                location=OpenApiParameter.HEADER,
                response=False,
                required=False,
            ),
            OpenApiParameter(
                name="X-Request-Id",
                type=str,
                location=OpenApiParameter.HEADER,
                response=True,
                required=True,
            ),
        )
    )

    return _extend_schema(
        operation_id=operation_id,
        parameters=parameters,
        request=request,
        responses=responses,
        auth=auth,
        description=description,
        summary=summary,
        deprecated=deprecated,
        tags=tags,
        filters=filters,
        exclude=exclude,
        operation=operation,
        methods=methods,
        versions=versions,
        examples=examples,
        extensions=extensions,
        callbacks=callbacks,
        external_docs=external_docs,
    )


def preprocessing_filter_spec(endpoints):
    filtered = []
    for path, path_regex, method, callback in endpoints:
        # Remove webhooks
        if "webhooks" not in path:
            filtered.append((path, path_regex, method, callback))
    return filtered

from typing import Any, Dict

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import StrOrPromise
from rest_framework import exceptions, status
from rest_framework.response import Response


class CustomException(Exception):
    _status = status.HTTP_400_BAD_REQUEST
    _detail = ""

    def __init__(self, detail: StrOrPromise | None = None):
        self.detail = detail if detail else self._detail

    def get_data(self):
        return {"detail": self.detail}

    @classmethod
    def get_status(cls):
        return cls._status


class Custom400Exception(CustomException):
    _status = status.HTTP_400_BAD_REQUEST


class Custom404Exception(CustomException):
    _status = status.HTTP_404_NOT_FOUND


class Custom500Exception(CustomException):
    _status = status.HTTP_500_INTERNAL_SERVER_ERROR


def custom_exception_handler(exc, context) -> Response | None:
    return ExceptionHandler(exc, context).run()


class ExceptionHandler:
    def __init__(self, exc: Exception, context: Any) -> None:
        self.exc = exc
        self.context = context

    def run(self) -> Response | None:
        exc = self._to_drf(self.exc)
        if self._should_not_handle(exc):
            return None
        if self._should_use_default_handler(exc):
            from rest_framework.views import exception_handler

            return exception_handler(exc, self.context)

        exc = self._fix_status_code(exc)
        exc = self._unhandled_to_drf(exc)
        data = self._format(exc)
        headers = self._get_headers(exc)
        return self._get_response(exc, data, headers)

    def _should_not_handle(self, exc: Exception) -> bool:
        return settings.DEBUG and not isinstance(exc, exceptions.APIException)

    def _should_use_default_handler(self, exc: Exception) -> bool:
        return isinstance(exc, exceptions.ValidationError) or isinstance(
            exc, exceptions.AuthenticationFailed
        )

    def _to_drf(self, exc: Exception) -> Exception:
        if isinstance(exc, Http404):
            return exceptions.NotFound()
        if isinstance(exc, PermissionDenied):
            return exceptions.PermissionDenied()
        if isinstance(exc, CustomException):
            new_exc = exceptions.APIException()
            new_exc.detail = exc.get_data().get("detail", "")
            new_exc.status_code = exc.get_status()
            return new_exc
        return exc

    def _fix_status_code(self, exc: Exception) -> Exception:
        if isinstance(exc, exceptions.AuthenticationFailed):
            exc.status_code = status.HTTP_401_UNAUTHORIZED
        return exc

    def _unhandled_to_drf(self, exc: Exception) -> exceptions.APIException:
        if not isinstance(exc, exceptions.APIException):
            return exceptions.APIException(detail=str(exc))
        return exc

    def _format(self, exc: exceptions.APIException) -> Dict:
        if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            detail = _("Произошла внутренняя ошибка. Пожалуйста, попробуйте позже.")
        else:
            detail = exc.detail
        return {"detail": detail}

    def _get_headers(self, exc: exceptions.APIException) -> Dict:
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait
        return headers

    def _get_response(
        self, exc: exceptions.APIException, data: Dict, headers: Dict
    ) -> Response:
        return Response(data, status=exc.status_code, headers=headers)

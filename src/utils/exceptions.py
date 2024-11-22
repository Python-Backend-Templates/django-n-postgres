import logging
import math
import traceback
from typing import Dict

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django_stubs_ext import StrOrPromise
from rest_framework import exceptions, status
from rest_framework.response import Response

http_logger = logging.getLogger("http")


class CustomException(Exception):
    _status = status.HTTP_400_BAD_REQUEST
    _detail = ""

    def __init__(self, detail: StrOrPromise | None = None):
        self.detail = detail if detail else self._detail

    def get_data(self) -> Dict[str, str]:
        return {"detail": self.detail}

    @classmethod
    def get_status(cls) -> int:
        return cls._status


class Custom400Exception(CustomException):
    _status = status.HTTP_400_BAD_REQUEST


class Custom404Exception(CustomException):
    _status = status.HTTP_404_NOT_FOUND


class Custom500Exception(CustomException):
    _status = status.HTTP_500_INTERNAL_SERVER_ERROR


class CustomThrottledException(exceptions.APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _("Request was throttled.")
    default_code = "throttled"
    extra_detail_1 = _("Ожидается доступность через {wait} секунду.")
    extra_detail_2 = _("Ожидается доступность через {wait} секунды.")
    extra_detail_3 = _("Ожидается доступность через {wait} секунд.")

    def __init__(
        self,
        wait: int | None = None,
        detail: StrOrPromise | None = None,
        code: int | None = None,
    ):
        if detail is None:
            detail = force_str(self.default_detail)
        if wait is not None:
            wait = math.ceil(wait)
            if wait % 10 == 1 and wait // 10 != 1:
                extra_detail = self.extra_detail_1
            elif wait % 10 in (2, 3, 4) and wait // 10 != 1:
                extra_detail = self.extra_detail_2
            else:
                extra_detail = self.extra_detail_3
            detail = " ".join(
                (
                    detail,
                    force_str(extra_detail.format(wait=wait)),
                )
            )
        self.wait = wait
        super().__init__(detail, code)


def custom_exception_handler(exc: Exception, context: Dict) -> Response | None:
    return ExceptionHandler(exc, context).run()


class ExceptionHandler:
    def __init__(self, exc: Exception, context: Dict) -> None:
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
        self._log(exc, data, headers)
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

        if isinstance(exc, exceptions.Throttled):
            detail = CustomThrottledException(
                wait=exc.wait,
                detail=None,
                code=exc.status_code,
            ).detail

        return {"detail": detail}

    def _get_headers(self, exc: exceptions.APIException) -> Dict:
        headers = {}
        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        if getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait
        return headers

    def _log(self, exc: exceptions.APIException, data: Dict, headers: Dict) -> None:
        if settings.DEBUG:
            return
        extra = {"data": data, "headers": headers}
        if exc.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
            http_logger.error("", extra=extra)
            return
        http_logger.critical(
            "",
            extra={
                **extra,
                "exception_message": traceback.format_exception_only(type(exc), exc),
                "exception_traceback": traceback.format_exc(),
            },
        )

    def _get_response(
        self, exc: exceptions.APIException, data: Dict, headers: Dict
    ) -> Response:
        return Response(data, status=exc.status_code, headers=headers)

import logging
import time
import traceback
from typing import Any, Callable, Dict
from urllib.parse import parse_qs

from django.conf import settings
from django.db import connection
from django.http import Http404, HttpRequest, HttpResponse
from rest_framework import exceptions

from utils.exceptions import CustomException

http_logger = logging.getLogger("http")


class ShowSQLMiddleware:
    def __init__(self, get_response: Callable) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if not settings.DEBUG:
            return response

        queries = connection.queries

        i = 0
        for query in queries:
            print(i, query)
            i += 1

        return response


class LogRequestMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start_time = time.time()
        response = self.get_response(request)
        self._log_request(request, response, start_time)
        return response

    def _log_request(
        self, request: HttpRequest, response: HttpResponse, start_time: float
    ) -> None:
        # логируем только "*/api/*" эндпоинты
        if "/api/" not in str(request.get_full_path()):
            return

        data = {
            "request_method": request.method,
            "request_path": request.get_full_path(),
            "query_params": parse_qs(request.META.get("QUERY_STRING", None)),
            "user_agent": request.META.get("HTTP_USER_AGENT", None),
            "status_code": response.status_code,
            "response_time": round((time.time() - start_time) * 1000, 3),
            "x_request_id": request.headers.get("X-Request-Id", None),
            "x_real_ip": request.headers.get("X-Real-Ip", None),
            "x_forwarded_for": request.headers.get("X-Forwarded-For", None),
        }

        # определим уровень лога на основе статуса ответа
        log_method_map = {
            1: http_logger.info,
            2: http_logger.info,
            3: http_logger.warning,
            4: http_logger.error,
            5: http_logger.critical,
        }

        log_method_map.get(response.status_code // 100, http_logger.info)(
            msg="", extra=data
        )

    def process_exception(self, request: HttpRequest, exception: Exception) -> None:
        if not settings.DEBUG:
            return
        extra: Dict[str, Any] = {
            "exception_message": traceback.format_exception_only(
                type(exception), exception
            )
        }
        if not isinstance(
            exception, (CustomException, Http404, exceptions.ValidationError)
        ):
            extra["exception_traceback"] = traceback.format_exc()
            http_logger.critical("", extra=extra)
            return
        http_logger.error("", extra=extra)


class RequestIdMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response: HttpResponse = self.get_response(request)
        response.headers["X-Request-Id"] = self._get_request_id(request)
        return response

    def _get_request_id(self, request: HttpRequest) -> str:
        return request.headers.get("X-Request-Id", "")

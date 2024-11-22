import logging
from dataclasses import asdict
from typing import Literal, NoReturn, Tuple

import requests
from django_stubs_ext import StrOrPromise
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import MaxRetryError
from urllib3.util.retry import Retry

from utils.entries import ThirdPartyRequest
from utils.exceptions import Custom400Exception, Custom404Exception
from utils.interfaces import IConvertDict, IThirdPartyAPICall, TResponse


class ThirdPartyAPICall(IThirdPartyAPICall[TResponse]):
    def __init__(
        self,
        url: str,
        method: Literal["get", "post"],
        convert: IConvertDict[TResponse],
        max_retries: int,
        retry_backoff_factor: float,
        timeout: int,
        error_message: StrOrPromise,
        logger: logging.Logger,
        log_headers: Tuple[str, ...] = tuple(),
    ) -> None:
        self.url = url
        self.method = method
        self.convert = convert
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor
        self.timeout = timeout
        self.error_message = error_message
        self.logger = logger
        self.log_headers = log_headers

    def __call__(self, entry: ThirdPartyRequest) -> TResponse:
        response = self._send(entry)
        response = self._validate_response(response, entry)
        result = self._result(response, entry)
        self._log(error=False, entry=entry, response=response)
        return result

    def _send(self, entry: ThirdPartyRequest) -> requests.Response | None:
        try:
            session = requests.Session()
            retry = Retry(
                connect=self.max_retries,
                backoff_factor=self.retry_backoff_factor,
            )
            adapter = HTTPAdapter(max_retries=retry)
            session.mount("https://", adapter)
            return getattr(session, self.method)(
                url=self._build_url(entry),
                data=entry.data,
                json=entry.json,
                headers=entry.headers,
                params=entry.params,
                timeout=self.timeout,
                cert=entry.cert,
                auth=(
                    HTTPBasicAuth(entry.basic_auth.username, entry.basic_auth.password)
                    if entry.basic_auth
                    else None
                ),
            )
        except (requests.RequestException, MaxRetryError) as e:
            self._error(entry=entry, exc=e)

    def _build_url(self, entry: ThirdPartyRequest) -> str:
        if not entry.path_params:
            return self.url
        url = self.url
        for param, value in entry.path_params.items():
            url = url.replace("{" + param + "}", value)
        return url

    def _validate_response(
        self,
        response: requests.Response | None,
        entry: ThirdPartyRequest,
    ) -> requests.Response:
        if response is None or response.status_code // 100 != 2:
            self._error(entry=entry, response=response)

        return response

    def _result(
        self,
        response: requests.Response,
        entry: ThirdPartyRequest,
    ) -> TResponse:
        try:
            obj = response.json()
        except requests.JSONDecodeError:
            obj = None

        try:
            return self.convert(obj)
        except ValueError as e:
            self._error(entry=entry, response=response, exc=e)

    def _log(
        self,
        *,
        error: bool,
        entry: ThirdPartyRequest,
        response: requests.Response | None = None,
        exc: Exception | None = None,
    ) -> None:
        msg = (
            f"API Call Failed - {str(exc)}."
            if exc
            else "API Call Failed." if error else "API Call Succeeded."
        )
        (self.logger.error if error else self.logger.info)(
            msg,
            extra={
                "url": self.url,
                "method": self.method,
                "request": asdict(entry),
                "status_code": response.status_code if response is not None else None,
                "response": (
                    response.content.decode()
                    if response is not None and response.content
                    else None
                ),
                "headers": (
                    {
                        header: response.headers.get(header, None)
                        for header in self.log_headers
                    }
                    if response
                    else None
                ),
            },
        )

    def _error(
        self,
        entry: ThirdPartyRequest,
        response: requests.Response | None = None,
        exc: Exception | None = None,
    ) -> NoReturn:
        self._log(error=True, entry=entry, response=response, exc=exc)

        exc_class = (
            Custom404Exception
            if response is not None and response.status_code == 404
            else Custom400Exception
        )
        raise exc_class(self.error_message)

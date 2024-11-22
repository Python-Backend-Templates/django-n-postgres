from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Generic, TypeVar

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

from utils.entries import ThirdPartyRequest

if TYPE_CHECKING:
    TResponse = TypeVar("TResponse", bound=DataclassInstance)
else:
    TResponse = TypeVar("TResponse")
T = TypeVar("T")


class IThirdPartyAPICall(ABC, Generic[TResponse]):
    @abstractmethod
    def __call__(self, entry: ThirdPartyRequest) -> TResponse:
        """
        ### Args:
            entry: dataclass with request data

        ### Raises:
            Custom400Exception - if there were an error sending request
                or response is not succesful;
            Custom404Exception - if response is not successful with 404 status code.
        """


class IConvertDict(ABC, Generic[T]):
    @abstractmethod
    def __call__(self, obj: Dict[str, Any] | None) -> T: ...

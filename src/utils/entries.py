from dataclasses import dataclass
from typing import TypeAlias, Dict, Any, Tuple, Mapping


Headers: TypeAlias = Dict[str, str]
Data: TypeAlias = Dict[str, str]
JSON: TypeAlias = Mapping[str, Any]
Params: TypeAlias = Dict[str, str]
Response: TypeAlias = Dict[str, Any]
PathParams: TypeAlias = Dict[str, str]
Cert: TypeAlias = Tuple[str, str]


@dataclass
class ThirdPartyBasicAuth:
    username: str
    password: str


@dataclass
class ThirdPartyRequest:
    headers: Headers | None = None
    data: Data | None = None
    json: JSON | None = None
    params: Params | None = None
    path_params: PathParams | None = None
    cert: Cert | None = None
    basic_auth: ThirdPartyBasicAuth | None = None


@dataclass
class ThirdPartyEmptyResponse:
    pass

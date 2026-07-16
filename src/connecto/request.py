"""Defines all requests that can be executed by a DataConnection, and associated
responses."""

from typing import Any
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class DataResponse(ABC):
    """ A generic response to a request """

@dataclass
class DataRequest(ABC):
    """ A generic request """

@dataclass
class DataSearchRequest(DataRequest):
    """ Search Request. Must be overwritten """

@dataclass
class DataSearchResponse(DataResponse):
    """ Search Response. Must be overwritten """


@dataclass
class DataCreateRequest(DataRequest):
    """ Create Request. Must be overwritten """


@dataclass
class DataCreateResponse(DataResponse):
    """ Create Response. Must be overwritten """


@dataclass
class DataDeleteRequest(DataRequest):
    """ Delete Request. Must be overwritten """


@dataclass
class DataDeleteResponse(DataResponse):
    """ Delete Response. Must be overwritten """


@dataclass
class DataUpdateRequest(DataRequest):
    """ Update Request. Must be overwritten """


@dataclass
class DataUpdateResponse(DataResponse):
    """ Update Response. Must be overwritten """


@dataclass
class DataSelectRequest(DataRequest):
    """ Select Request. Must be overwritten """

@dataclass
class DataSelectResponse(DataResponse):
    """ Select Response. Must be overwritten """

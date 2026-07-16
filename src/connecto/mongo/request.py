"""Defines all requests that can be executed by a MongoConnection, and associated
responses."""

from typing import Any
from dataclasses import dataclass
from ..request import (
    DataCreateRequest,
    DataDeleteRequest,
    DataCreateResponse,
    DataDeleteResponse,
    DataSearchRequest,
    DataSearchResponse,
    DataSelectRequest,
    DataSelectResponse,
    DataUpdateRequest,
    DataUpdateResponse,
)

@dataclass
class MongoSearchRequest(DataSearchRequest):
    """Search the value at `path` within the YAML file.

    `path` is specified as in utils.nested_data_path
    """

    _id: str


@dataclass
class MongoSearchResponse(DataSearchResponse):
    """Value found in a YAML file from a MongoSearchRequest."""

    value: Any


@dataclass
class MongoCreateRequest(DataCreateRequest):
    """Create a new item at `path` with value in the YAML file.

    created_id might be used by item mappers to specify the new ID of the item
    to create. It can be ignored when creating single attributes.

    `path` is specified as in utils.nested_data_path
    """

    obj: Any


@dataclass
class MongoCreateResponse(DataCreateResponse):
    """Returns the id of the created item for a base request. Else, the response
    can be ignored."""

    _id: str


@dataclass
class MongoDeleteRequest(DataDeleteRequest):
    """Delete the value at `path` within the YAML file.

    """

    _id: str


@dataclass
class MongoDeleteResponse(DataDeleteResponse):
    """Nothing to return."""


@dataclass
class MongoUpdateRequest(DataUpdateRequest):
    """Updates the item at `path` with value in the YAML file.

    `path` is specified as in utils.nested_data_path
    """
    _id: str
    obj: Any


@dataclass
class MongoUpdateResponse(DataUpdateResponse):
    """Nothing to return."""


@dataclass
class MongoSelectRequest(DataSelectRequest):
    """Selects all items at path, so path must be the path to the root of the
    item collection.

    The YAML database does not support any selection mecanism, so the select
    filter is always ignored and all items are returned.
    """

    filter: Any

@dataclass
class MongoSelectResponse(DataSelectResponse):
    """Returns all items found in a YAML file from a MongoSelectRequest."""

    values: list[ dict ]

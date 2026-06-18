"""Defines all requests that can be executed by a YamlConnection, and associated
responses."""

from typing import Any
from dataclasses import dataclass


@dataclass
class YamlSearchRequest:
    """Search the value at `path` within the YAML file.

    `path` is specified as in utils.nested_data_path
    """

    path: list[str | int]


@dataclass
class YamlSearchResponse:
    """Value found in a YAML file from a YamlSearchRequest."""

    value: Any


@dataclass
class YamlCreateRequest:
    """Create a new item at `path` with value in the YAML file.

    created_id might be used by item mappers to specify the new ID of the item
    to create. It can be ignored when creating single attributes.

    `path` is specified as in utils.nested_data_path
    """

    path: list[str | int]
    value: Any
    created_id: str | None = None


@dataclass
class YamlCreateResponse:
    """Returns the id of the created item for a base request. Else, the response
    can be ignored."""

    created_id: str


@dataclass
class YamlDeleteRequest:
    """Delete the value at `path` within the YAML file.

    `path` is specified as in utils.nested_data_path
    """

    path: list[str | int]


@dataclass
class YamlDeleteResponse:
    """Nothing to return."""


@dataclass
class YamlUpdateRequest:
    """Updates the item at `path` with value in the YAML file.

    `path` is specified as in utils.nested_data_path
    """

    path: list[str | int]
    value: Any


@dataclass
class YamlUpdateResponse:
    """Nothing to return."""


@dataclass
class YamlSelectRequest:
    """Selects all items at path, so path must be the path to the root of the
    item collection.

    The YAML database does not support any selection mecanism, so the select
    filter is always ignored and all items are returned.
    """

    path: list[str | int]


@dataclass
class YamlSelectResponse:
    """Returns all items found in a YAML file from a YamlSelectRequest."""

    values: dict[str | int, Any]

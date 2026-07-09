"""Provides the implementation of a DatabaseConnection to a YAML file."""

import pathlib
from yaml import load, dump, Loader, Dumper
from ..utils.nested_data_path import find, update, delete

from ..connection import DatabaseConnection
from .request import (
    YamlSearchRequest,
    YamlSearchResponse,
    YamlCreateRequest,
    YamlCreateResponse,
    YamlDeleteRequest,
    YamlDeleteResponse,
    YamlUpdateRequest,
    YamlSelectRequest,
    YamlSelectResponse,
)
from ..error import ItemNotFound


class YamlConnection(DatabaseConnection):
    """Database connection used to perform operations on a YAML file.

    The `yaml_path` parameter allows to specify where is the root of the
    collection of items within the YAML file, if it's not the root of the file
    itself. See utils.nested_data_path for how to specify the path as a list of
    str / int.

    For example, if `database.yaml` looks like
    ```yaml
    config:
      some: "value"
      data: 1
    users:
      collection:
        1: <user 1>
        2: <user 2>
        ...
    ```
    the connection should be initialized as
    ```python
    YamlConnection("database.yaml", ["users", "collection"])
    ```


    :param file_path: Path to the YAML database
    :param yaml_path: A nested data path to the root of the collection within
    the file.
    """

    def __init__(self, file_path, yaml_path=None):
        self.file_path = pathlib.Path(file_path)
        if yaml_path is None:
            self.yaml_path = []
        else:
            self.yaml_path = yaml_path

    def execute_search(self, request: YamlSearchRequest):
        with open(self.file_path, "r", encoding="utf_8") as yaml_database:
            database = load(yaml_database.read(), Loader=Loader)
            try:
                return YamlSearchResponse(
                    # The request search path is relative to the base YAML path
                    find(database, self.yaml_path + request.path),
                )
            except KeyError as e:
                raise ItemNotFound(request.path, self.file_path) from e

    def execute_create(self, request: YamlCreateRequest):
        database = None
        with open(self.file_path, "r", encoding="utf_8") as yaml_database:
            # Init database as an empty dict if the file is empty
            database = load(yaml_database.read(), Loader=Loader) or {}

        # The path of the item to update is relative to the base YAML path
        update(
            database,
            self.yaml_path + request.path,
            request.value,
        )

        with open(self.file_path, "w", encoding="utf_8") as yaml_database:
            yaml_database.write(dump(database, Dumper=Dumper))
        return YamlCreateResponse(request.created_id)

    def execute_delete(self, request: YamlDeleteRequest):
        database = None
        with open(self.file_path, "r", encoding="utf_8") as yaml_database:
            # Init database as an empty dict if the file is empty
            database = load(yaml_database.read(), Loader=Loader) or {}

        try:
            # The path of the item to delete is relative to the base YAML path
            delete(database, self.yaml_path + request.path)
        except KeyError:
            # Deleting an object that do not exist is not an error
            pass

        with open(self.file_path, "w", encoding="utf_8") as yaml_database:
            yaml_database.write(dump(database, Dumper=Dumper))
        return YamlDeleteResponse()

    def execute_update(self, request: YamlUpdateRequest):
        database = None
        with open(self.file_path, "r", encoding="utf_8") as yaml_database:
            # Init database as an empty dict if the file is empty
            database = load(yaml_database.read(), Loader=Loader) or {}

        # The path of the item to update is relative to the base YAML path
        update(
            database,
            self.yaml_path + request.path,
            request.value,
        )

        with open(self.file_path, "w", encoding="utf_8") as yaml_database:
            yaml_database.write(dump(database, Dumper=Dumper))
        return YamlDeleteResponse()

    def execute_select(self, request: YamlSelectRequest):
        database = None
        with open(self.file_path, "r", encoding="utf_8") as yaml_database:
            # Init database as an empty dict if the file is empty
            database = load(yaml_database.read(), Loader=Loader) or {}

            items = {}

            # Consider items at base yaml_path
            for key, value in find(database, self.yaml_path).items():
                # Gets the value at request.path within each item
                items[key] = find(value, request.path)
            return YamlSelectResponse(items)

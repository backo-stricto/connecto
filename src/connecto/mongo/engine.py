"""Provides a specialization of the DatabaseEngine for a YAML database."""

from ..engine import DatabaseEngine
from .connection import MongoConnection
from .item import MongoItem
from .attribute import MongoAttribute


class MongoEngine(DatabaseEngine):
    """Extends the DatabaseEngine with convenient default for YAML.

    `MongoEngine("database.yaml")` will initialize the engine with a default
    `MongoItem()` (items mapped by keys and default initialization without
    model), assuming the collection is stored at the root of the `database.yaml`
    file.

    :param file_path: Path to the YAML database
    :param yaml_path: A nested data path to the root of the collection within
    the file. See MongoConnection.
    :param database_item: Item loaded from the database
    """

    def __init__(self, connection_string:str, collection_name:str, model={}, **kwargs):
        super().__init__(MongoConnection(connection_string, collection_name, **kwargs), MongoItem(model=model))





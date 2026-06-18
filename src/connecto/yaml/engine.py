"""Provides a specialization of the DatabaseEngine for a YAML database."""

from ..engine import DatabaseEngine
from .connection import YamlConnection
from .item import YamlItem


class YamlEngine(DatabaseEngine):
    """Extends the DatabaseEngine with convenient default for YAML.

    `YamlEngine("database.yaml")` will initialize the engine with a default
    `YamlItem()` (items mapped by keys and default initialization without
    model), assuming the collection is stored at the root of the `database.yaml`
    file.

    :param file_path: Path to the YAML database
    :param yaml_path: A nested data path to the root of the collection within
    the file. See YamlConnection.
    :param database_item: Item loaded from the database
    """

    def __init__(self, file_path, database_item=YamlItem(), yaml_path=None):
        super().__init__(YamlConnection(file_path, yaml_path), database_item)

"""Provides a specialization of the DatabaseItem for a YAML database."""

from ..item import DatabaseItem
from .mapper import MapById


class MongoItem(DatabaseItem):
    """Extends the DatabaseItem with convenient defaults for mongo.

    The model is a nested structure of list / dict / tuple with MongoAttributes
    or generic attributes (e.g. ReverseRef) as leafs. It can also be a single
    attribute.

    For example:
    ```python
    MongoItem(model={"login": MongoAttribute(["name"])}
    ```
    """

    def __init__(self, item_mapper=MapById(), model={}):
        super().__init__(item_mapper, model)

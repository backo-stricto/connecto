"""Provides a specialization of the DatabaseItem for a YAML database."""

from ..item import DatabaseItem
from .mapper import MapByKey


class YamlItem(DatabaseItem):
    """Extends the DatabaseItem with convenient defaults for YAML.

    By default, items are mapped by keys with UUID4 ids for new items, and the
    model is empty. This means all fields will be read and written from / to the
    YAML file for each item.

    The model is a nested structure of list / dict / tuple with YamlAttributes
    or generic attributes (e.g. ReverseRef) as leafs. It can also be a single
    attribute.

    For example:
    ```python
    YamlItem(model={"login": YamlAttribute(["name"])}
    ```
    """

    def __init__(self, item_mapper=MapByKey(), model=None):
        if model is None:
            super().__init__(item_mapper, {})
        else:
            super().__init__(item_mapper, model)

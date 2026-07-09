"""Provides reverse refs implementations."""

import functools
from stricto import List, Dict, GenericType, SFilter

from .attribute import DatabaseAttribute


class InvalidReverseRef(Exception):
    """Exception raised if a ReverseRef finds more than one item matching the
    reference filter, which means the filter or the item is ill formed.
    """

    def __init__(self, reverse_ref, loaded_filter, found_items):
        super().__init__(
            self,
            f"The reverse ref at {reverse_ref.attribute_path} "
            f"cannot be resolved because too many items was found "
            f"using filter {loaded_filter} but a single referenced "
            f"item is expected. "
            f"The elements found was: {found_items}",
        )


def _compile_stricto_item_dict(item):
    compiled_item = {}
    for key, attribute in item.items():
        if isinstance(attribute, dict):
            compiled_item[key] = _compile_stricto_item_dict(attribute)
        elif isinstance(attribute, list):
            compiled_item[key] = List(GenericType())
        else:
            compiled_item[key] = GenericType()
    return Dict(compiled_item)


def _compile_stricto_item(item):
    if isinstance(item, dict):
        stricto_item = _compile_stricto_item_dict(item)
    elif isinstance(item, list):
        stricto_item = List(GenericType())
    else:
        stricto_item = GenericType()
    stricto_item.set(item)
    return stricto_item


class ReverseRef(DatabaseAttribute):
    """A generic reverse reference attribute that can be used for any
    connection.

    A reverse reference can be used to fill an attribute with the id of a remote
    item matching an item filter.

    The `select_engine` is used to perform a select on the referenced items. It
    embeds the DatabaseItem and the DatabaseConnection that will be used to
    query remote items. More particularly, the reverse reference attribute will
    be filled with ids returned by the item mapper of the referenced
    DatabaseItem, so the value of the reverse reference can be controlled
    configuring the item mapper.

    The item_filter is itself a DatabaseItem that can reference attributes of
    the current item. For example:
    ```python
    item_filter = ("$.users", Operator.CONTAINS, Attribute("username")
    ```
    means the attribute "username" of the current item must be contained in the
    `users` field of the referenced item to resolve the reverse reference.

    The user must ensure the item_filter will always find at most one referenced
    item, else an InvalidReverseRef exception will be raised when the reference
    is loaded.
    """

    def __init__(self, select_engine, item_filter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.select_engine = select_engine
        self.item_filter = item_filter

    def set_default_connection(self, connection):
        """Overrides the set_default_connection method so the default connection
        set for the attribute is also used for the item filter.

        The user can still define a custom connection for the ReverseRef
        attribute itself and the attributes of the item filter.
        """
        super().set_default_connection(connection)
        self.item_filter.set_default_connection(connection)

    def search_request(self, base_request, _id):
        # Build requests required to load the filter. search_request returns a
        # tuple (base_request, <attribute_requests>).
        # The value is converted to a list so it can be handled by the calling
        # database engine.
        return list(self.item_filter.search_request(_id))

    def load(self, _base_response, attribute_response):
        # Loads the SFilter item from the responses of search_request
        loaded_filter = SFilter(
            *self.item_filter.load(
                # Base response
                attribute_response[0],
                # Responses for attributes of the filter
                attribute_response[1],
            )
        )
        # Use the select_engine to select referenced items.
        # Each item is converted to a backo item with GenericTypes so the loaded
        # filter can be executed on selected items
        select_items = [
            (_id, _compile_stricto_item(item))
            for _id, item in self.select_engine.select(loaded_filter)
        ]
        # Applies the loaded filter to items, because it is not guaranteed that
        # the loaded_filter will be completly resolved by select_engine.select
        matching_items = list(
            filter(functools.partial(_filter_item, loaded_filter), select_items)
        )

        if len(matching_items) > 1:
            raise InvalidReverseRef(self, loaded_filter, matching_items)
        if len(matching_items) == 0:
            return None

        return matching_items[0][0]


def _filter_item(item_filter, item):
    return item_filter.check(item[1])

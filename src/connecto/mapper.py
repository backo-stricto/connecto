from typing import Any
from .request import (
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
"""Provides the specification of the ItemMapper interface."""


class ItemMapper:
    """Base requests handling to support each database operations.

    Each ItemMapper implementation is specific to a database type, but several
    ItemMappers might be defined for each database, depending on how data is
    structured in the database.

    For example, in the case of an LDAP database, the `MapByDN` item mapper
    might identify items using their DN, while the MapByAttribute(search_base,
    "id") might identify items using the "id" attribute of each entry within the
    search_base.

    How to map database specific ids to item _ids is actually a core feature of
    the ItemMapper, as ID mapping is the minimum requirement of each base
    request.

    For example, it defines how the `_id` provided to the search_request must be
    used to build the base request that will be used by all attributes to manage
    the item associated to `_id`.

    For example, a `MapSqlKey("table", "id")` SQL item mapper will likely
    generate a search base request that is equivalent to `SELECT * FROM "table"
    WHERE "id" == _id`. Each SQL attribute in the model might then specialize
    selected fields in the request.

    Any DatabaseAttribute should be compatible with any ItemMapper as long as
    they use the same database request types.
    """

    def created_id(self, create_response:DataCreateResponse) -> str:
        """Retrieve the id of the created item from the response of the base
        create request.

        The id is a string that can be later provided to search_request(),
        delete_request() or update_request() methods to work on the item.

        :param create_response: Response of the base create request. Its type
        is implementation dependent.
        """
        raise NotImplementedError("This ItemMapper does not support item creation")

    def search_request(self, _id) -> DataSearchRequest:
        """Builds a request that can be used as a base request to search the
        item associated to _id.

        :param _id: ID of the item to search
        :return: A search request. Its type is implementation dependent.
        """
        raise NotImplementedError("This ItemMapper does not support item search")

    def create_request(self, item_value) -> DataCreateRequest:
        """Builds a request that can be used as a base request to create a new
        item with the specified value.

        :param item_value: Initial values of attributes for the new item
        :return: A create request. Its type is implementation dependent.
        """
        raise NotImplementedError("This ItemMapper does not support item creation")

    def delete_request(self, _id) -> DataDeleteRequest:
        """Builds a request that can be used as a base request to delete a new
        item with the specified value.

        :param _id: ID of the item to delete
        :return: A delete request. Its type is implementation dependent.
        """
        raise NotImplementedError("This ItemMapper does not support item deletion")

    def update_request(self, _id, item_value) -> DataUpdateRequest:
        """Builds a request that can be used as a base request to update the
        item associated to _id with the specified value.

        :param _id: ID of the item to update
        :param item_value: New values of attributes for the item
        :return: A delete request. Its type is implementation dependent.
        """
        raise NotImplementedError("This ItemMapper does not support item update")

    def select_request(self, item_filter) -> DataSelectRequest:
        """Builds a request that can be used as a base request to select items
        matching the specified filter.

        The request does not need to return exactly the list of items matching
        the filter, but must ensure all items in the database matching the
        filter can be loaded from the response. This means a request returning
        all items will be a valid response for any filter.

        :param item_filter: Stricto item filter
        """
        raise NotImplementedError("This ItemMapper does not support select")

    def load(self, init_value: Any, _base_response: DataSearchResponse):
        """Loads the base JSON-like dict representation of an item from the
        response of the base request.

        Database attributes will then increment this representation.

        By default, the empty init value is returned.

        The provided init value is an empty structure corresponding the model
        currently loaded. It's either an empty list (`[]`) or an empty dict
        (`{}`).

        Notice that tuples are loaded as lists (and later converted to tuples by
        the DatabaseItem itself) and that the load() method of the item mapper
        is not called for single attribute models as it won't have any sense
        (because the loaded model value is only the value of the attribute).

        This method can be overidden to load a base value from the
        base_response, but the returned value must always correspond to the type
        of the init value.
        """
        return init_value

    def load_items(self, _base_init_factory, _base_response: DataSelectResponse):
        """Loads a list of base JSON-like structure representation of items from
        response of the base select request.

        Database attributes will then increment the representation of each item.
        The items can also be completely loaded from the base_response.

        This method must be implemented to return a list of tuple `(_id,
        <init_value>)` for **all** items included in the base response, so that
        each one can be loaded from the model. Entries not returned by this
        method won't be considered.

        The base init factory is a callable without argument that can be used to
        produce empty init values for each entry. It produces either empty lists
        (`[]`), empty dicts (`{}`) or `None` depending on the type of the model.

        Lists are used to initialize tuple and list models, dicts for dict
        models, and None for single attribute models.

        Implementations are free to build any init value for each item, but its
        type must always correspond to the type of values produced by the base
        init factory.
        """

    def select_response(self, _id, base_request_response: DataSelectResponse, attribute_responses: DataSelectResponse) -> tuple [ DataSelectResponse, DataSelectResponse ]:
        """Extracts responses from a select response that can be used to load()
        the item associated to `_id`.

        Responses to select requests are expected to include data for several
        items. For the base request it will be many base items, for attribute
        responses it will be values for many attributes.

        This method extracts the data that can be used to load() each item and
        attribute from each response.

        The returned objects must be valid parameters for the
        DatabaseItem.load() method, so that the item associated to `_id` is
        loaded as if it were from a search request for that specific `_id`.

        :param _id: ID of the item that must be loaded
        :param base_request_response: Response to a select request, including
        base data for all items
        :param base_attribute_response: Response to a select request, including
        data of a specific attribute for all items
        """
        return base_request_response, attribute_responses

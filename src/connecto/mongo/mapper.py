"""Provides implementations of ItemMappers for a YAML database."""

import copy
from typing import Any
from ..item import ItemMapper

from .request import (
    MongoSearchRequest,
    MongoCreateRequest,
    MongoCreateResponse,
    MongoDeleteRequest,
    MongoUpdateRequest,
    MongoSelectRequest,
    MongoSearchResponse,
    MongoSelectResponse,
)

class MapById(ItemMapper):
    """Item mapper that can be used to manage a collection of items organized in
    a YAML dict as `{_id: <item value>}`.

    :param generate_id: A callable used to generated unique IDs for new items.
    :param empty_init: If true, the mapper will load all item values included in
    the YAML database, even if they are not explicitly defined as attributes in
    the model of the item.
    """

    def __init__(self):
        pass

    def created_id(self, create_response: MongoCreateResponse):
        return create_response._id

    def search_request(self, _id:str )-> MongoSearchRequest:
        return MongoSearchRequest(_id)

    def create_request(self, item_value)-> MongoCreateRequest:
        # Use a deep copy of values for the base request so that attributes can
        # modify it later without side effects
        return MongoCreateRequest(copy.deepcopy(item_value))

    def delete_request(self, _id)-> MongoDeleteRequest:
        return MongoDeleteRequest(_id)

    def update_request(self, _id, item_value)-> MongoUpdateRequest:
        # Use a deep copy of values for the base request so that attributes can
        # modify it later without side effects
        return MongoUpdateRequest(_id, copy.deepcopy(item_value))

    def load(self, init_value:Any, base_search_response):

        return base_search_response.value

    def select_request(self, _item_filter:Any) -> MongoSelectRequest:
        # Use [] as path to select the complete item at each key
        return MongoSelectRequest([])

    def load_items(self, init_factory, base_request_response: MongoSelectResponse)-> list[ dict ]:
        if self.empty_init:
            return [
                (_id, init_factory()) for _id in base_request_response.values.keys()
            ]
        return list(base_request_response.values.items())

    def select_response(
        self,
        _id,
        base_request_response: MongoSelectResponse,
        attribute_responses: MongoSelectResponse,
    )-> tuple [ MongoSelectResponse, MongoSelectResponse ]:
        # Base response for the item associated to _id
        base_response = MongoSearchResponse(base_request_response.values[_id])

        # Response for the attribute of the item associated to _id
        item_attribute_response = None
        if attribute_responses is not None:
            item_attribute_response = MongoSearchResponse(
                attribute_responses.values[_id]
            )
        return base_response, item_attribute_response

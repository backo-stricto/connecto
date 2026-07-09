"""Provides implementations of ItemMappers for a YAML database."""

import uuid
import copy

from ..item import ItemMapper

from .request import (
    YamlSearchRequest,
    YamlCreateRequest,
    YamlCreateResponse,
    YamlDeleteRequest,
    YamlUpdateRequest,
    YamlSelectRequest,
    YamlSearchResponse,
    YamlSelectResponse,
)


def uuid4():
    """Generates a UUID4 id."""
    return str(uuid.uuid4())


class MapByKey(ItemMapper):
    """Item mapper that can be used to manage a collection of items organized in
    a YAML dict as `{_id: <item value>}`.

    :param generate_id: A callable used to generated unique IDs for new items.
    :param empty_init: If true, the mapper will load all item values included in
    the YAML database, even if they are not explicitly defined as attributes in
    the model of the item.
    """

    def __init__(self, generate_id=uuid4, empty_init=False):
        self.generate_id = generate_id
        self.empty_init = empty_init

    def created_id(self, create_response: YamlCreateResponse):
        return create_response.created_id

    def search_request(self, _id):
        return YamlSearchRequest([_id])

    def create_request(self, item_value):
        _id = self.generate_id()
        # Use a deep copy of values for the base request so that attributes can
        # modify it later without side effects
        return YamlCreateRequest([_id], copy.deepcopy(item_value), _id)

    def delete_request(self, _id):
        return YamlDeleteRequest([_id])

    def update_request(self, _id, item_value):
        # Use a deep copy of values for the base request so that attributes can
        # modify it later without side effects
        return YamlUpdateRequest([_id], copy.deepcopy(item_value))

    def load(self, init_value, base_search_response):
        if self.empty_init:
            return init_value
        return base_search_response.value

    def select_request(self, _item_filter):
        # Use [] as path to select the complete item at each key
        return YamlSelectRequest([])

    def load_items(self, init_factory, base_request_response: YamlSelectResponse):
        if self.empty_init:
            return [
                (_id, init_factory()) for _id in base_request_response.values.keys()
            ]
        return list(base_request_response.values.items())

    def select_response(
        self,
        _id,
        base_request_response: YamlSelectResponse,
        attribute_responses: YamlSelectResponse,
    ):
        # Base response for the item associated to _id
        base_response = YamlSearchResponse(base_request_response.values[_id])

        # Response for the attribute of the item associated to _id
        item_attribute_response = None
        if attribute_responses is not None:
            item_attribute_response = YamlSearchResponse(
                attribute_responses.values[_id]
            )
        return base_response, item_attribute_response

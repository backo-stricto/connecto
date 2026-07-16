"""Implementation of the DatabaseItem"""

from .mapper import ItemMapper
from .attribute import DatabaseAttribute
from .connection import DatabaseConnection

class DatabaseItem:
    """A DatabaseItem specifies how data should be loaded from the database to
    produce a valid JSON-like dict that could be provided to load a backo Item.

    Even if its structure might look similar to the associated backo Item, it is
    not a duplication of information contained in the backo Item, as the purpose
    of the DatabaseItem is only to specify how to produce a valid JSON-like dict
    from raw items contained in the database.

    The Item specifies the structure of the object with fields and types, and the
    DatabaseItem specifies how to retrieve them from a specific database.
    """

    def __init__(self, item_mapper: ItemMapper, model: dict):
        """
        The `item_mapper` specifies how to build base requests for each
        operation. Each attribute of the model is then allowed to modify the
        base request en retrieve data from its response, in addition to their
        own requests.

        The `model` is a dict mapping JSON fields to specification of database
        attributes. Here is a simple example for LDAP:
        ```
        {
            "name": Attribute("uid"),
            "description": Attribute("description")
        }
        ```
        With this example, the DatabaseItem will load() the JSON-like dict by
        loading values of `name` and `description` fields from the `uid` and
        `description` attributes of the LDAP entry associated to the item. The
        `item_mapper` (e.g. `MapByDN`) defined how to retrieve the entry itself.

        :param item_mapper: Specifies how to map database entries to backo `_id`s.
        :param model: Dictionnary of database attributes
        """
        self.item_mapper = item_mapper
        self.model = model

        # Informs each attribute of its path within the model
        _set_attribute_paths(self.model, [])

        # It is set by the DatabaseEngine using
        # set_default_connection
        self.connection = None

    def set_default_connection(self, connection:DatabaseConnection):
        """Sets the connection that will be used to perform base requests and
        attribute requests, unless the attribute is already associated to a
        specific connection.
        """
        self.connection = connection
        _set_model_connection(self.model, connection)

    def search_request(self, _id):
        """Builds a set of search requests that will be able to load all the
        attributes required to load the item represented by `_id`.

        Responses obtained by the DatabaseEngine will then be passed to the
        load() method of the DatabaseItem.

        :param _id: ID of the item to search
        """

        # Builds request required by the `item_mapper` to perform the `base`
        # initialization of the `DatabaseItem` instance associated to an `_id`
        base_request = self.item_mapper.search_request(_id)
        base_request.connection = self.connection

        #  Builds additional requests required to initialize all attributes of
        #  the `model`. Each attribute is allowed to either modify the
        #  `base_request`, build new requests or do nothing.
        model_requests = None
        if isinstance(self.model, dict):
            model_requests = {}
            _request_dict(
                base_request, model_requests, self.model, _search_request, _id
            )
        elif isinstance(self.model, (tuple, list)):
            model_requests = []
            _request_list(
                base_request, model_requests, self.model, _search_request, _id
            )
        else:
            model_requests = _search_request(self.model, base_request, _id)

        return base_request, model_requests

    def create_request(self, item_value):
        """Builds a set of create requests that will be able to load all the
        attributes required to load the item represented by `_id`.

        Responses obtained by the DatabaseEngine will then be passed to the
        created_id() method of the DatabaseItem.

        :param item_value: JSON-like dict with values of attributes of the new
        item. Its structure must be compatible with the model.
        """

        # Builds request required by the `item_mapper` to create the `item` with
        # value `item_value` and initialize its _id
        base_request = self.item_mapper.create_request(item_value)
        base_request.connection = self.connection

        #  Builds additional requests required to create all attributes of the
        #  `model`. Each attribute is allowed to either modify the
        #  `base_request`, build a new request or do nothing.
        model_requests = None
        if isinstance(self.model, dict):
            model_requests = {}
            _request_dict_with_values(
                base_request, model_requests, self.model, item_value, _create_request
            )
        elif isinstance(self.model, (tuple, list)):
            model_requests = []
            _request_list_with_values(
                base_request, model_requests, self.model, item_value, _create_request
            )
        else:
            model_requests = _create_request(self.model, base_request, item_value)

        return base_request, model_requests

    def delete_request(self, _id):
        """Builds a set of delete requests that will be able to delete all the
        attributes of the item represented by `_id` (and the item itself).

        :param _id: ID of the item to delete
        """

        # Builds request required by the `item_mapper` to delete the item
        # corresponding to _id
        base_request = self.item_mapper.delete_request(_id)
        base_request.connection = self.connection

        #  Builds additional requests required to delete all attributes of the
        #  `DatabaseItem`. Each attribute is allowed to either modify the
        #  `base_request`, build a new request or do nothing.
        model_requests = None
        if isinstance(self.model, dict):
            model_requests = {}
            _request_dict(
                base_request, model_requests, self.model, _delete_request, _id
            )
        elif isinstance(self.model, (tuple, list)):
            model_requests = []
            _request_list(
                base_request, model_requests, self.model, _delete_request, _id
            )
        else:
            model_requests = _delete_request(self.model, base_request, _id)

        return base_request, model_requests

    def update_request(self, _id, item_value):
        """Builds a set of update requests that will be able to update the
        attributes of the item represented by `_id` with values from
        `item_value`.

        :param _id: ID of the item to update
        :param item_value: JSON-like dict with values of attributes of the new
        item. Its structure must be compatible with the model.
        """

        # Builds request required by the `item_mapper` to create the `item` with
        # value `item_value` and initialize its _id
        base_request = self.item_mapper.update_request(_id, item_value)
        base_request.connection = self.connection

        #  Builds additional requests required to create all attributes of the
        #  `model`. Each attribute is allowed to either modify the
        #  `base_request`, build a new request or do nothing.
        model_requests = None
        if isinstance(self.model, dict):
            model_requests = {}
            _request_dict_with_values(
                base_request,
                model_requests,
                self.model,
                item_value,
                _update_request,
                _id,
            )
        elif isinstance(self.model, (tuple, list)):
            model_requests = []
            _request_list_with_values(
                base_request,
                model_requests,
                self.model,
                item_value,
                _update_request,
                _id,
            )
        else:
            model_requests = _update_request(self.model, base_request, _id, item_value)

        return base_request, model_requests

    def select_request(self, item_filter):
        """Builds a set of select requests that will be able to return the
        list of items _at least_ matching the specified filter.

        :param item_value: A Stricto SFilter to convert to database requests
        """

        # Builds request required by the `item_mapper` to perform the `base`
        # selection of `DatabaseItem` instances
        base_request = self.item_mapper.select_request(item_filter)
        base_request.connection = self.connection

        #  Builds additional requests required to initialize all attributes of
        #  the `model`. Each attribute is allowed to either modify the
        #  `base_request`, build new requests or do nothing.
        model_requests = None
        if isinstance(self.model, dict):
            model_requests = {}
            _request_dict(
                base_request, model_requests, self.model, _select_request, item_filter
            )
        elif isinstance(self.model, (list, tuple)):
            model_requests = []
            _request_list(
                base_request, model_requests, self.model, _select_request, item_filter
            )
        else:
            model_requests = _select_request(self.model, base_request, item_filter)

        return base_request, model_requests

    def load(self, base_request_response, attribute_responses):
        """Loads the item in a JSON-like structure from the database response.

        The response has been obtained by the DatabaseEngine from the request
        provided by search_request().
        """

        if isinstance(self.model, list):
            item = self.item_mapper.load([], base_request_response)
            _load_list(base_request_response, attribute_responses, item, self.model)
        elif isinstance(self.model, tuple):
            # The tuple value is initialized as list, and converted to a tuple
            # once the list has been filled with values.
            item = self.item_mapper.load([], base_request_response)
            _load_list(base_request_response, attribute_responses, item, self.model)
            item = tuple(item)
        elif isinstance(self.model, dict):
            item = self.item_mapper.load({}, base_request_response)
            _load_dict(base_request_response, attribute_responses, item, self.model)
        else:
            # Nothing to load from the item_mapper if the model is a single
            # attribute, as the single would systematically override the init
            # value of the item mapper
            item = self.model.load(base_request_response, attribute_responses)
        return item

    def load_items(self, base_request_response, attribute_responses):
        """Loads a list of items in a JSON-like list from the database response.

        The response has been obtained by the DatabaseEngine from the request
        provided by select_request().
        """
        if isinstance(self.model, dict):
            items = self.item_mapper.load_items(lambda: {}, base_request_response)
        elif isinstance(self.model, (tuple, list)):
            items = self.item_mapper.load_items(lambda: [], base_request_response)
        else:
            items = self.item_mapper.load_items(lambda: None, base_request_response)

        loaded_items = items
        for i, (_id, item) in enumerate(items):
            if isinstance(self.model, list):
                # Loads directly into item, that is referenced in both items and
                # loaded_items
                _load_items_list(
                    self.item_mapper,
                    _id,
                    base_request_response,
                    attribute_responses,
                    item,
                    self.model,
                )
            elif isinstance(self.model, tuple):
                # Loads into item
                _load_items_list(
                    self.item_mapper,
                    _id,
                    base_request_response,
                    attribute_responses,
                    item,
                    self.model,
                )
                # Replaces the item with the loaded tuple
                loaded_items[i] = (_id, tuple(item))
            elif isinstance(self.model, dict):
                # Loads directly into item, that is referenced in both items and
                # loaded_items
                _load_items_dict(
                    self.item_mapper,
                    _id,
                    base_request_response,
                    attribute_responses,
                    item,
                    self.model,
                )
            else:
                # Replaces the item with the loaded attribute
                loaded_items[i] = (
                    _id,
                    self.model.load(
                        *_select_responses(
                            self.item_mapper,
                            _id,
                            base_request_response,
                            attribute_responses,
                        )
                    ),
                )
        return loaded_items

    def created_id(self, base_create_response):
        """Returns the value that should be used as _id from the response of the
        create operation.
        """
        return self.item_mapper.created_id(base_create_response)


# Recursion algorithms


def _requests_with_connection(requests, connection):
    """request_method wrapper to set the connection on all requests.

    requests is a nested structure of requests.
    """
    _set_requests_connection(requests, connection)
    return requests


def _set_requests_connection(requests, connection):
    """Sets connection on each request of a nested request structure."""
    if isinstance(requests, list):
        for request in requests:
            _set_requests_connection(request, connection)
    elif isinstance(requests, dict):
        for request in requests.values():
            _set_requests_connection(request, connection)
    elif requests is not None:
        requests.connection = connection


def _search_request(attribute, base_request, _id):
    """Builds search requests as attribute.search_request(base_request, _id) and
    sets connection on all requests.
    """
    return _requests_with_connection(
        attribute.search_request(base_request, _id), attribute.connection
    )


def _create_request(attribute, base_request, value):
    """Builds create requests as attribute.create_request(base_request, value)
    and sets connection on all requests.
    """
    return _requests_with_connection(
        attribute.create_request(base_request, value), attribute.connection
    )


def _delete_request(attribute, base_request, _id):
    """Builds delete requests as attribute.delete_request(base_request, _id) and
    sets connection on all requests.
    """
    return _requests_with_connection(
        attribute.delete_request(base_request, _id), attribute.connection
    )


def _update_request(attribute, base_request, _id, value):
    """Builds update requests as attribute.update_request(base_request, _id,
    value) and sets connection on all requests.
    """
    return _requests_with_connection(
        attribute.update_request(base_request, _id, value), attribute.connection
    )


def _select_request(attribute, base_request, item_filter):
    """Builds select requests as attribute.select_request(base_request,
    item_filter) and sets connection on all requests.
    """
    return _requests_with_connection(
        attribute.select_request(base_request, item_filter), attribute.connection
    )


def _set_attribute_paths(attributes, current_path):
    """Sets attribute path on each attribute of a model."""
    if isinstance(attributes, (list, tuple)):
        i = 0
        for attribute in attributes:
            _set_attribute_paths(attribute, current_path + [i])
            i += 1
    elif isinstance(attributes, dict):
        for key, attribute in attributes.items():
            _set_attribute_paths(attribute, current_path + [key])
    elif isinstance(attributes, DatabaseAttribute):
        attributes.set_attribute_path(current_path)


def _set_model_connection(attributes, connection):
    """Sets connection on each attribute of a model."""
    if isinstance(attributes, (list, tuple)):
        for attribute in attributes:
            _set_model_connection(attribute, connection)
    elif isinstance(attributes, dict):
        for attribute in attributes.values():
            _set_model_connection(attribute, connection)
    elif isinstance(attributes, DatabaseAttribute):
        attributes.set_default_connection(connection)


def _request_list(base_request, request_list, attributes_list, request_method, *args):
    """Appends items to the request list using request_method, processing nested
    structures as required.

    request_method is called as request_method(attribute, base_request, *args)
    when reaching a leaf attribute.
    """
    for attribute in attributes_list:
        if isinstance(attribute, (list, tuple)):
            requests = []
            _request_list(base_request, requests, attribute, request_method, *args)
            request_list.append(requests)
        elif isinstance(attribute, dict):
            requests = {}
            _request_dict(base_request, requests, attribute, request_method, *args)
            request_list.append(requests)
        elif isinstance(attribute, DatabaseAttribute):
            request_list.append(request_method(attribute, base_request, *args))


def _request_dict(base_request, request_dict, attributes_dict, request_method, *args):
    """Builds entries in the request_dict using request_method, processing
    nested structures as required.

    request_method is called as request_method(attribute, base_request, *args)
    when reaching a leaf attribute.
    """
    for key, attribute in attributes_dict.items():
        if isinstance(attribute, (list, tuple)):
            requests = []
            _request_list(base_request, requests, attribute, request_method, *args)
            request_dict[key] = requests
        elif isinstance(attribute, dict):
            requests = {}
            _request_dict(base_request, requests, attribute, request_method, *args)
            request_dict[key] = requests
        elif isinstance(attribute, DatabaseAttribute):
            request_dict[key] = request_method(attribute, base_request, *args)


def _request_list_with_values(
    base_request, request_list, attributes_list, values, request_method, *args
):
    """Appends items to the request_list using request_method, processing nested
    structures as required.

    request_method is called as request_method(attribute, base_request, *args,
    value) when reaching a leaf attribute. `value` is the item at the same index
    as attribute in the `attributes_list`.
    """
    for attribute, value in zip(attributes_list, values):
        if isinstance(attribute, (list, tuple)):
            requests = []
            _request_list_with_values(
                base_request, requests, attribute, value, request_method, *args
            )
            request_list.append(requests)
        elif isinstance(attribute, dict):
            requests = {}
            _request_dict_with_values(
                base_request, requests, attribute, value, request_method, *args
            )
            request_list.append(requests)
        elif isinstance(attribute, DatabaseAttribute):
            request_list.append(request_method(attribute, base_request, *args, value))


def _request_dict_with_values(
    base_request, request_dict, attributes_dict, values, request_method, *args
):
    """Builds entries in the request_dict using request_method, processing
    nested structures as required.

    request_method is called as request_method(attribute, base_request, *args,
    value) when reaching a leaf attribute. `value` is the value associated to
    the same key as the `attribute` in `attributes_dict`. If no such value
    exist, the `request_method` is called with None as `value`.
    """
    for key, attribute in attributes_dict.items():
        if isinstance(attribute, (list, tuple)):
            requests = []
            _request_list_with_values(
                base_request,
                requests,
                attribute,
                values.get(key),
                request_method,
                *args,
            )
            request_dict[key] = requests
        elif isinstance(attribute, dict):
            requests = {}
            _request_dict_with_values(
                base_request,
                requests,
                attribute,
                values.get(key),
                request_method,
                *args,
            )
            request_dict[key] = requests
        elif isinstance(attribute, DatabaseAttribute):
            request_dict[key] = request_method(
                attribute, base_request, *args, values.get(key)
            )


def _load_list(base_request_response, attributes_responses, item_list, attributes_list):
    """Loads a list of values into item_list from base_request_response and
    attributes_responses, processing nested structures as required.

    Value of the list are loaded from lead attributes so that the item at index
    i is loaded as attribute.load(base_request_response, response) where
    attribute=attributes_list[i] and response=attributes_responses[i].
    """
    j = 0
    for attribute in attributes_list:
        if isinstance(attribute, dict):
            item_value = {}
            _load_dict(
                base_request_response,
                attributes_responses[j],
                item_value,
                attribute,
            )
            item_list.append(item_value)
            j += 1
        elif isinstance(attribute, list):
            item_value = []
            _load_list(
                base_request_response,
                attributes_responses[j],
                item_value,
                attribute,
            )
            item_list.append(item_value)
            j += 1
        elif isinstance(attribute, tuple):
            item_value = []
            _load_list(
                base_request_response,
                attributes_responses[j],
                item_value,
                attribute,
            )
            item_list.append(tuple(item_value))
            j += 1
        elif isinstance(attribute, DatabaseAttribute):
            item_list.append(
                attribute.load(base_request_response, attributes_responses[j])
            )
            j += 1
        else:
            # Constant
            item_list.append(attribute)
            # Do not increment response index because no response is included
            # for constants


def _load_dict(base_request_response, attributes_responses, item_dict, attributes_node):
    """Loads a dict of values into item_dict from base_request_response and
    attributes_responses, processing nested structures as required.

    Value of the dict are loaded from lead attributes so that the item at key is
    loaded as attribute.load(base_request_response, response) where
    attribute=attributes_list[key] and response=attributes_responses[key].
    """
    for key, attribute in attributes_node.items():
        if isinstance(attribute, dict):
            item_dict[key] = {}
            _load_dict(
                base_request_response,
                attributes_responses[key],
                item_dict[key],
                attribute,
            )
        elif isinstance(attribute, list):
            item_dict[key] = []
            _load_list(
                base_request_response,
                attributes_responses[key],
                item_dict[key],
                attribute,
            )
        elif isinstance(attribute, tuple):
            tuple_values = []
            _load_list(
                base_request_response,
                attributes_responses[key],
                tuple_values,
                attribute,
            )
            item_dict[key] = tuple(tuple_values)
        elif isinstance(attribute, DatabaseAttribute):
            item_dict[key] = attribute.load(
                base_request_response, attributes_responses[key]
            )
        else:
            item_dict[key] = attribute


def _load_items_list(
    item_mapper,
    _id,
    base_request_response,
    attributes_responses,
    item_list,
    attributes_list,
):
    j = 0
    for attribute in attributes_list:
        if isinstance(attribute, dict):
            item_value = {}
            _load_items_dict(
                item_mapper,
                _id,
                base_request_response,
                attributes_responses[j],
                item_value,
                attribute,
            )
            item_list.append(item_value)
            j += 1
        elif isinstance(attribute, list):
            item_value = []
            _load_items_list(
                item_mapper,
                _id,
                base_request_response,
                attributes_responses[j],
                item_value,
                attribute,
            )
            item_list.append(item_value)
            j += 1
        elif isinstance(attribute, tuple):
            item_value = []
            _load_items_list(
                item_mapper,
                _id,
                base_request_response,
                attributes_responses[j],
                item_value,
                attribute,
            )
            item_list.append(tuple(item_value))
            j += 1
        elif isinstance(attribute, DatabaseAttribute):
            item_list.append(
                attribute.load(
                    *_select_responses(
                        item_mapper, _id, base_request_response, attributes_responses[j]
                    )
                )
            )
            j += 1
        else:
            item_list.append(attribute)


def _load_items_dict(
    item_mapper,
    _id,
    base_request_response,
    attributes_responses,
    item_dict,
    attributes_node,
):
    for key, attribute in attributes_node.items():
        if isinstance(attribute, dict):
            item_dict[key] = {}
            _load_items_dict(
                item_mapper,
                _id,
                base_request_response,
                attributes_responses[key],
                item_dict[key],
                attribute,
            )
        elif isinstance(attribute, list):
            item_dict[key] = []
            _load_items_list(
                item_mapper,
                _id,
                base_request_response,
                attributes_responses[key],
                item_dict[key],
                attribute,
            )
        elif isinstance(attribute, tuple):
            item_value = []
            _load_items_list(
                item_mapper,
                _id,
                base_request_response,
                attributes_responses[key],
                item_value,
                attribute,
            )
            item_dict[key] = tuple(item_value)
        elif isinstance(attribute, DatabaseAttribute):
            item_dict[key] = attributes_node[key].load(
                *_select_responses(
                    item_mapper, _id, base_request_response, attributes_responses[key]
                )
            )
        else:
            item_dict[key] = attribute


def _select_responses_list(item_mapper, _id, base_request_response, response):
    select_responses = []
    base_select_response = None
    for value in response:
        if isinstance(value, dict):
            base_select_response, select_response = _select_responses_dict(
                item_mapper, _id, base_request_response, value
            )
            select_responses.append(select_response)
        elif isinstance(value, list):
            base_select_response, select_response = _select_responses_list(
                item_mapper, _id, base_request_response, value
            )
            select_responses.append(select_response)
        else:
            base_select_response, select_response = item_mapper.select_response(
                _id, base_request_response, value
            )
            select_responses.append(select_response)
    return base_select_response, select_responses


def _select_responses_dict(item_mapper, _id, base_request_response, response):
    select_responses = {}
    base_select_response = None
    for key, value in response.items():
        if isinstance(value, dict):
            base_select_response, select_response = _select_responses_dict(
                item_mapper, _id, base_request_response, value
            )
            select_responses[key] = select_response
        elif isinstance(value, list):
            base_select_response, select_response = _select_responses_list(
                item_mapper, _id, base_request_response, value
            )
            select_responses[key] = select_response
        else:
            base_select_response, select_response = item_mapper.select_response(
                _id, base_request_response, value
            )

            select_responses[key] = select_response
    return base_select_response, select_responses


def _select_responses(item_mapper, _id, base_request_response, response):
    if isinstance(response, dict):
        return _select_responses_dict(item_mapper, _id, base_request_response, response)
    if isinstance(response, list):
        return _select_responses_list(item_mapper, _id, base_request_response, response)
    return item_mapper.select_response(_id, base_request_response, response)

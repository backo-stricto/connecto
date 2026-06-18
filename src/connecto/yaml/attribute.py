"""Provides the implementation of a DatabaseAttribute for a YAML database."""

from ..attribute import DatabaseAttribute
from ..utils.nested_data_path import find, update, delete, equal_path


class YamlAttribute(DatabaseAttribute):
    """A YamlAttribute can be used within a model to specify where the value is
    located within the YAML database.

    The specified path is relative to the root of each item. The path is a list
    of dict keys / list indexes, as specified in utils.nested_data_path.

    :param path: Path to the attribute with the YAML representation of the item.
    """

    def __init__(self, path=None):
        super().__init__()
        self.path = path

        # True if and only if the value of the attribute is at a path that is
        # different from the path of the attribute within the model.
        self.path_to_self = path is None

    def set_attribute_path(self, attribute_path):
        super().set_attribute_path(attribute_path)

        if self.path is None:
            # No path was specified by the user, so use attribute path as path.
            self.path = self.attribute_path
            self.path_to_self = True
        elif equal_path(self.attribute_path, self.path):
            # A path was specified but it's actually the same as the path of the
            # attribute in the model
            self.path_to_self = True

    def search_request(self, base_request, _id):
        # Nothing to do, the requested field will already be included in the
        # response of the base_request, that include the complete object
        # associated to _id
        pass

    def load(self, base_response, _attribute_response):
        # _attribute_response is None, because no request was returned by
        # search_request. But the field can be retrieved from the response of
        # the base request
        value = find(base_response.value, self.path)

        if not self.path_to_self:
            # The value must be deleted from the response so this field is not
            # included in the generated JSON-like dict
            delete(base_response.value, self.path)
        return value

    def create_request(self, base_request, value):
        if not self.path_to_self:
            # Removes the replaced path from the original user item
            delete(base_request.value, self.attribute_path)

        # Adds the value of the attribute to the base create request
        update(base_request.value, self.path, value)

    def update_request(self, base_request, _id, value):
        if not self.path_to_self:
            # Removes the replaced path from the original user item
            delete(base_request.value, self.attribute_path)

        # Adds the value of the attribute to the base create request
        update(base_request.value, self.path, value)

    def delete_request(self, base_request, _id):
        # Nothing to do, the complete item will be deleted by the base request
        pass

    def select_request(self, base_request, item_filter):
        # Nothing to do, the requested field will already be included in the
        # response of the base_request, that include the complete object
        # associated to each item
        pass

"""DatabaseItem delete operation tests"""

import unittest
from unittest.mock import MagicMock

from hamcrest import (
    assert_that,
    contains_exactly,
    has_entries,
    has_properties,
)

from connecto.item import DatabaseItem
from connecto.attribute import DatabaseAttribute
from connecto.mapper import ItemMapper
from connecto.connection import DatabaseConnection


class TestDatabaseItemDelete(unittest.TestCase):
    # pylint: disable=R0801
    """Tests delete requests building depending on the complexity of the model."""

    def setUp(self):
        self.connection = MagicMock(spec=DatabaseConnection)
        self.base_request = MagicMock(connection=None)
        self.item_mapper = MagicMock(spec=ItemMapper)
        self.item_mapper.delete_request.return_value = self.base_request

        self.attribute_requests = [MagicMock() for _ in range(6)]
        self.attribute_mocks = [
            MagicMock(
                spec=DatabaseAttribute,
                request=self.attribute_requests[i],
                connection=self.connection,
            )
            for i in range(6)
        ]
        for i in range(6):
            self.attribute_mocks[i].delete_request.return_value = (
                self.attribute_requests[i]
            )

    def test_delete_request_single_attribute_model(self):
        """Tests the validity of built delete requests for a single attribute
        model that return no request."""
        database_item = DatabaseItem(self.item_mapper, self.attribute_mocks[0])
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        assert_that(
            self.attribute_requests[0], has_properties(connection=self.connection)
        )

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        assert_that(
            self.attribute_mocks[0].delete_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.item_mapper.delete_request.return_value, "mock_id"
                    )
                )
            ),
        )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                self.attribute_requests[0],
            ),
        )

    def test_delete_request_with_none_request(self):
        """Tests the validity of built delete requests for a single attribute model."""
        self.attribute_mocks[0].delete_request.return_value = None

        database_item = DatabaseItem(self.item_mapper, self.attribute_mocks[0])
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        assert_that(
            self.attribute_mocks[0].delete_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.item_mapper.delete_request.return_value, "mock_id"
                    )
                )
            ),
        )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                None,
            ),
        )

    def test_delete_request_simple_tuple_model(self):
        """Tests the validity of built delete requests for a tuple model."""
        database_item = DatabaseItem(
            self.item_mapper,
            tuple(self.attribute_mocks),
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                contains_exactly(*self.attribute_requests),
            ),
        )

    def test_delete_request_simple_list_model(self):
        """Tests the validity of built delete requests for a list model."""
        database_item = DatabaseItem(
            self.item_mapper,
            self.attribute_mocks,
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                contains_exactly(*self.attribute_requests),
            ),
        )

    def test_delete_request_simple_dict_model(self):
        """Tests the validity of built delete requests for a dict model."""
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "login": self.attribute_mocks[0],
                "name": self.attribute_mocks[1],
                "contact": self.attribute_mocks[2],
            },
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:3]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks[:3]:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                has_entries(
                    {
                        "login": self.attribute_requests[0],
                        "name": self.attribute_requests[1],
                        "contact": self.attribute_requests[2],
                    }
                ),
            ),
        )

    def test_delete_request_with_complex_nested_attributes(self):
        """Tests the validity of built delete requests for a model with
        attributes nested in dicts, lists and tuples.
        """
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "name": self.attribute_mocks[0],
                "nested": {
                    "data": (
                        [self.attribute_mocks[1], self.attribute_mocks[2]],
                        self.attribute_mocks[3],
                        {"nested_data": self.attribute_mocks[4]},
                    ),
                    "time": self.attribute_mocks[5],
                },
            },
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                has_entries(
                    {
                        "name": self.attribute_requests[0],
                        "nested": has_entries(
                            {
                                "data": contains_exactly(
                                    [
                                        self.attribute_requests[1],
                                        self.attribute_requests[2],
                                    ],
                                    self.attribute_requests[3],
                                    {"nested_data": self.attribute_requests[4]},
                                ),
                                "time": self.attribute_requests[5],
                            }
                        ),
                    }
                ),
            ),
        )

    def test_delete_multiple_request_attribute(self):
        """Tests the validity of built delete requests for a model with
        attributes that require multiple requests nested in dicts and lists.
        """

        # Overrides setUp defaults
        self.attribute_mocks[0].delete_request.return_value = {
            "request1": self.attribute_requests[0],
            "request2": self.attribute_requests[1],
        }
        self.attribute_mocks[1].delete_request.return_value = [
            self.attribute_requests[2],
            {"req1": self.attribute_requests[3], "req2": self.attribute_requests[4]},
        ]

        database_item = DatabaseItem(
            self.item_mapper,
            {
                "foo": self.attribute_mocks[0],
                "nested": {"bar": self.attribute_mocks[1]},
            },
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:5]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks[:2]:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                has_entries(
                    {
                        "foo": has_entries(
                            {
                                "request1": self.attribute_requests[0],
                                "request2": self.attribute_requests[1],
                            }
                        ),
                        "nested": has_entries(
                            {
                                "bar": contains_exactly(
                                    self.attribute_requests[2],
                                    has_entries(
                                        {
                                            "req1": self.attribute_requests[3],
                                            "req2": self.attribute_requests[4],
                                        }
                                    ),
                                )
                            }
                        ),
                    }
                ),
            ),
        )

    def test_delete_request_simple_tuple_model_with_constants(self):
        """Tests the validity of built delete requests for a tuple model with
        constants."""
        database_item = DatabaseItem(
            self.item_mapper,
            (self.attribute_mocks[0], "constant", self.attribute_mocks[1]),
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:2]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks[:2]:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                contains_exactly(*self.attribute_requests[:2]),
            ),
        )

    def test_delete_request_simple_list_model_with_constants(self):
        """Tests the validity of built delete requests for a list model with
        constants."""
        database_item = DatabaseItem(
            self.item_mapper,
            [self.attribute_mocks[0], "constant", self.attribute_mocks[1]],
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:2]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks[:2]:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                contains_exactly(*self.attribute_requests[:2]),
            ),
        )

    def test_delete_request_simple_dict_model_with_constants(self):
        """Tests the validity of built delete requests for a dict model."""
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "login": self.attribute_mocks[0],
                "contact": self.attribute_mocks[1],
            },
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:2]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks[:2]:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                has_entries(
                    {
                        "login": self.attribute_requests[0],
                        "contact": self.attribute_requests[1],
                    }
                ),
            ),
        )

    def test_delete_request_with_complex_nested_attributes_and_constants(self):
        """Tests the validity of built delete requests for a model with
        attributes and constants nested in dicts, lists and tuples.
        """
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "name": self.attribute_mocks[0],
                "nested": {
                    "data": (
                        [self.attribute_mocks[1], self.attribute_mocks[2]],
                        "constant",
                        {"nested_data": self.attribute_mocks[3]},
                    ),
                    "time": "now",
                },
            },
        )
        # Connection used for the base request
        database_item.connection = self.connection

        delete_requests = database_item.delete_request("mock_id")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:4]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )
        for attribute in self.attribute_mocks[:4]:
            assert_that(
                attribute.delete_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.delete_request.return_value, "mock_id"
                        )
                    )
                ),
            )

        assert_that(
            delete_requests,
            contains_exactly(
                self.item_mapper.delete_request.return_value,
                has_entries(
                    {
                        "name": self.attribute_requests[0],
                        "nested": has_entries(
                            {
                                "data": contains_exactly(
                                    [
                                        self.attribute_requests[1],
                                        self.attribute_requests[2],
                                    ],
                                    {"nested_data": self.attribute_requests[3]},
                                ),
                            }
                        ),
                    }
                ),
            ),
        )

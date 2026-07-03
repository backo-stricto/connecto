"""DatabaseItem create operation tests"""

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


class TestDatabaseItemCreate(unittest.TestCase):
    # pylint: disable=R0801
    """Tests create requests building depending on the complexity of the model."""

    def setUp(self):
        self.connection = MagicMock(spec=DatabaseConnection)
        self.base_request = MagicMock(connection=None)
        self.item_mapper = MagicMock(spec=ItemMapper)
        self.item_mapper.create_request.return_value = self.base_request

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
            self.attribute_mocks[i].create_request.return_value = (
                self.attribute_requests[i]
            )

    def test_create_request_single_attribute_model(self):
        """Tests the validity of built create requests for a single attribute model."""
        database_item = DatabaseItem(
            self.item_mapper,
            self.attribute_mocks[0],
        )
        # Connection used for the base request
        database_item.connection = self.connection

        create_requests = database_item.create_request("new_value")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        assert_that(
            self.attribute_requests[0], has_properties(connection=self.connection)
        )

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("new_value"))),
        )
        assert_that(
            self.attribute_mocks[0].create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.item_mapper.create_request.return_value, "new_value"
                    )
                )
            ),
        )

        assert_that(
            create_requests,
            contains_exactly(
                self.item_mapper.create_request.return_value, self.attribute_requests[0]
            ),
        )

    def test_create_request_with_none_request(self):
        """Tests the validity of built create requests for a single attribute
        model that return no request."""

        # Overrides setUp returned request
        self.attribute_mocks[0].create_request.return_value = None

        database_item = DatabaseItem(
            self.item_mapper,
            self.attribute_mocks[0],
        )
        # Connection used for the base request
        database_item.connection = self.connection

        create_requests = database_item.create_request("new_value")

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("new_value"))),
        )
        assert_that(
            self.attribute_mocks[0].create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.item_mapper.create_request.return_value, "new_value"
                    )
                )
            ),
        )

        assert_that(
            create_requests,
            contains_exactly(self.item_mapper.create_request.return_value, None),
        )

    def test_create_request_simple_tuple_model(self):
        """Tests the validity of built create requests for a tuple model."""
        database_item = DatabaseItem(
            self.item_mapper,
            model=tuple(self.attribute_mocks[:3]),
        )
        # Connection used for the base request
        database_item.connection = self.connection

        create_requests = database_item.create_request(
            ("new_login", "new_name", "new_contact")
        )

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:3]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        contains_exactly(
                            "new_login",
                            "new_name",
                            "new_contact",
                        )
                    )
                )
            ),
        )
        for attribute, value in zip(
            self.attribute_mocks[:3], ["new_login", "new_name", "new_contact"]
        ):
            assert_that(
                attribute.create_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.create_request.return_value, value
                        )
                    )
                ),
            )

        assert_that(
            create_requests,
            contains_exactly(
                self.item_mapper.create_request.return_value,
                contains_exactly(*self.attribute_requests[:3]),
            ),
        )

    def test_create_request_simple_list_model(self):
        """Tests the validity of built create requests for a list model."""
        database_item = DatabaseItem(
            self.item_mapper,
            self.attribute_mocks[:3],
        )
        # Connection used for the base request
        database_item.connection = self.connection

        create_requests = database_item.create_request(
            ["new_login", "new_name", "new_contact"]
        )

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:3]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        contains_exactly(
                            "new_login",
                            "new_name",
                            "new_contact",
                        )
                    )
                )
            ),
        )
        for attribute, value in zip(
            self.attribute_mocks[:3], ["new_login", "new_name", "new_contact"]
        ):
            assert_that(
                attribute.create_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.create_request.return_value, value
                        )
                    )
                ),
            )

        assert_that(
            create_requests,
            contains_exactly(
                self.item_mapper.create_request.return_value,
                contains_exactly(*self.attribute_requests[:3]),
            ),
        )

    def test_create_request_simple_dict_model(self):
        """Tests the validity of built create requests for a dict model."""
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

        create_requests = database_item.create_request(
            {"login": "new_login", "name": "new_name", "contact": "new_contact"}
        )

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:3]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        has_entries(
                            {
                                "login": "new_login",
                                "name": "new_name",
                                "contact": "new_contact",
                            }
                        )
                    )
                )
            ),
        )
        for attribute, value in zip(
            self.attribute_mocks[:3], ["new_login", "new_name", "new_contact"]
        ):
            assert_that(
                attribute.create_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.create_request.return_value, value
                        )
                    )
                ),
            )

        assert_that(
            create_requests,
            contains_exactly(
                self.item_mapper.create_request.return_value,
                has_entries(
                    {
                        "login": self.attribute_requests[0],
                        "name": self.attribute_requests[1],
                        "contact": self.attribute_requests[2],
                    }
                ),
            ),
        )

    def test_create_with_missing_dict_value(self):
        """Tests the validity of built create requests for a dict model with
        missing values in user input."""
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

        create_requests = database_item.create_request(
            # Missing value for contact
            {"login": "new_login", "name": "new_name"}
        )

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:3]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        has_entries(
                            {
                                "login": "new_login",
                                "name": "new_name",
                            }
                        )
                    )
                )
            ),
        )
        for attribute, value in zip(
            # The contact attribute should still be created with None. In a
            # real use case, the real attribute will decide what to do with
            # missing value.
            self.attribute_mocks[:3],
            ["new_login", "new_name", None],
        ):
            assert_that(
                attribute.create_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.create_request.return_value, value
                        )
                    )
                ),
            )

        assert_that(
            create_requests,
            contains_exactly(
                self.item_mapper.create_request.return_value,
                has_entries(
                    {
                        "login": self.attribute_requests[0],
                        "name": self.attribute_requests[1],
                        "contact": self.attribute_requests[2],
                    }
                ),
            ),
        )

    def test_create_request_with_complex_nested_attributes(self):
        """Tests the validity of built create requests for a model with
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

        create_requests = database_item.create_request(
            {
                "name": "new_name",
                "nested": {
                    "data": (
                        [13, 12],
                        "data_1",
                        {"nested_data": "new_nested_value"},
                    ),
                    "time": "new_time",
                },
            }
        )

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        has_entries(
                            {
                                "name": "new_name",
                                "nested": has_entries(
                                    {
                                        "data": contains_exactly(
                                            contains_exactly(13, 12),
                                            "data_1",
                                            has_entries(
                                                {"nested_data": "new_nested_value"}
                                            ),
                                        ),
                                        "time": "new_time",
                                    }
                                ),
                            }
                        )
                    )
                )
            ),
        )
        for attribute, value in zip(
            self.attribute_mocks,
            [
                "new_name",
                13,
                12,
                "data_1",
                "new_nested_value",
                "new_time",
            ],
        ):
            assert_that(
                attribute.create_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.create_request.return_value, value
                        )
                    )
                ),
            )

        assert_that(
            create_requests,
            contains_exactly(
                self.item_mapper.create_request.return_value,
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

    def test_create_multiple_request_attribute(self):
        """Tests the validity of built create requests for a model with
        attributes that require multiple requests nested in dicts and lists.
        """

        # Overrides setUp defaults
        self.attribute_mocks[0].create_request.return_value = {
            "request1": self.attribute_requests[0],
            "request2": self.attribute_requests[1],
        }
        self.attribute_mocks[1].create_request.return_value = [
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

        create_requests = database_item.create_request(
            {"foo": "foo_value", "nested": {"bar": ["bar_value_1", "bar_value_2"]}}
        )

        # As a side effect, the connection must have been set up on all requests
        # returned in search_requests
        assert_that(self.base_request, has_properties(connection=self.connection))
        for request in self.attribute_requests[:5]:
            assert_that(request, has_properties(connection=self.connection))

        assert_that(
            self.item_mapper.create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        has_entries(
                            {
                                "foo": "foo_value",
                                "nested": has_entries(
                                    {"bar": ["bar_value_1", "bar_value_2"]}
                                ),
                            }
                        )
                    )
                )
            ),
        )
        for attribute, value in zip(
            self.attribute_mocks[:2],
            ["foo_value", contains_exactly("bar_value_1", "bar_value_2")],
        ):
            assert_that(
                attribute.create_request.call_args_list,
                contains_exactly(
                    has_properties(
                        args=contains_exactly(
                            self.item_mapper.create_request.return_value, value
                        )
                    )
                ),
            )

        assert_that(
            create_requests,
            contains_exactly(
                self.item_mapper.create_request.return_value,
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

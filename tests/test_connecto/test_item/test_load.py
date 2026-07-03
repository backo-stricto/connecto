"""DatabaseItem load tests"""

import unittest
from unittest.mock import MagicMock

from hamcrest import (
    assert_that,
    contains_exactly,
    has_entries,
    has_properties,
    equal_to,
)

from connecto.item import DatabaseItem
from connecto.attribute import DatabaseAttribute
from connecto.mapper import ItemMapper


class TestDatabaseItemLoad(unittest.TestCase):
    # pylint: disable=R0801

    """Tests item loading depending on the complexity of the model."""

    def setUp(self):
        self.base_response = MagicMock()
        self.item_mapper = MagicMock(spec=ItemMapper)

        self.attribute_responses = [MagicMock() for _ in range(6)]
        self.attribute_mocks = [
            MagicMock(spec=DatabaseAttribute, response=self.attribute_responses[i])
            for i in range(6)
        ]

    def test_load_single_attribute_model(self):
        """Tests database item loading for a single attribute model."""
        database_item = DatabaseItem(self.item_mapper, self.attribute_mocks[0])

        self.attribute_mocks[0].load.return_value = "John Doe"

        # Real call to the method under test
        item = database_item.load(self.base_response, self.attribute_responses[0])

        assert_that(
            self.item_mapper.load.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(self.base_response))),
        )

        assert_that(
            self.attribute_mocks[0].load.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.base_response, self.attribute_responses[0]
                    )
                )
            ),
        )

        assert_that(
            item,
            equal_to("John Doe"),
        )

    def test_load_simple_tuple_model(self):
        """Tests database item loading for a tuple model."""
        database_item = DatabaseItem(self.item_mapper, tuple(self.attribute_mocks[:3]))

        self.item_mapper.load.return_value = []
        self.attribute_mocks[0].load.return_value = "jdoe"
        self.attribute_mocks[1].load.return_value = "John Doe"
        self.attribute_mocks[2].load.return_value = [
            "mail1@example.org",
            "mail2@jdoe.fr",
        ]

        # Real call to the method under test
        item = database_item.load(self.base_response, self.attribute_responses[:3])

        assert_that(
            self.item_mapper.load.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(self.base_response))),
        )

        for attribute, response in zip(
            self.attribute_mocks[:3], self.attribute_responses[:3]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    has_properties(args=contains_exactly(self.base_response, response))
                ),
            )

        assert_that(
            item,
            contains_exactly(
                "jdoe",
                "John Doe",
                contains_exactly("mail1@example.org", "mail2@jdoe.fr"),
            ),
        )

    def test_load_simple_list_model(self):
        """Tests database item loading for a list model."""
        database_item = DatabaseItem(self.item_mapper, self.attribute_mocks[:3])

        self.item_mapper.load.return_value = []
        self.attribute_mocks[0].load.return_value = "jdoe"
        self.attribute_mocks[1].load.return_value = "John Doe"
        self.attribute_mocks[2].load.return_value = [
            "mail1@example.org",
            "mail2@jdoe.fr",
        ]

        # Real call to the method under test
        item = database_item.load(self.base_response, self.attribute_responses[:3])

        assert_that(
            self.item_mapper.load.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(self.base_response))),
        )

        for attribute, response in zip(
            self.attribute_mocks[:3], self.attribute_responses[:3]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    has_properties(args=contains_exactly(self.base_response, response))
                ),
            )

        assert_that(
            item,
            contains_exactly(
                "jdoe",
                "John Doe",
                contains_exactly("mail1@example.org", "mail2@jdoe.fr"),
            ),
        )

    def test_load_simple_dict_model(self):
        """Tests database item loading for a dict model."""
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "login": self.attribute_mocks[0],
                "name": self.attribute_mocks[1],
                "contact": self.attribute_mocks[2],
            },
        )

        self.item_mapper.load.return_value = {}
        self.attribute_mocks[0].load.return_value = "jdoe"
        self.attribute_mocks[1].load.return_value = "John Doe"
        self.attribute_mocks[2].load.return_value = [
            "mail1@example.org",
            "mail2@jdoe.fr",
        ]

        # Real call to the method under test
        item = database_item.load(
            self.base_response,
            {
                "login": self.attribute_responses[0],
                "name": self.attribute_responses[1],
                "contact": self.attribute_responses[2],
            },
        )

        assert_that(
            self.item_mapper.load.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(self.base_response))),
        )

        for attribute, response in zip(
            self.attribute_mocks[:3], self.attribute_responses[:3]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    has_properties(args=contains_exactly(self.base_response, response))
                ),
            )

        assert_that(
            item,
            has_entries(
                {
                    "login": "jdoe",
                    "name": "John Doe",
                    "contact": contains_exactly("mail1@example.org", "mail2@jdoe.fr"),
                }
            ),
        )

    def test_load_item_with_complex_nested_attributes(self):
        """Tests database item loading for a model with attributes nested in
        dicts, lists and tuples.
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

        self.item_mapper.load.return_value = {}
        self.attribute_mocks[0].load.return_value = "jdoe"
        self.attribute_mocks[1].load.return_value = 13
        self.attribute_mocks[2].load.return_value = 12
        self.attribute_mocks[3].load.return_value = "some_value"
        self.attribute_mocks[4].load.return_value = "nested_data_value"
        self.attribute_mocks[5].load.return_value = "now"

        # Real call to the method under test
        item = database_item.load(
            self.base_response,
            {
                "name": self.attribute_responses[0],
                "nested": {
                    "data": (
                        [self.attribute_responses[1], self.attribute_responses[2]],
                        self.attribute_responses[3],
                        {"nested_data": self.attribute_responses[4]},
                    ),
                    "time": self.attribute_responses[5],
                },
            },
        )

        assert_that(
            self.item_mapper.load.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(self.base_response))),
        )

        for attribute, response in zip(self.attribute_mocks, self.attribute_responses):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    has_properties(args=contains_exactly(self.base_response, response))
                ),
            )

        assert_that(
            item,
            has_entries(
                {
                    "name": "jdoe",
                    "nested": has_entries(
                        {
                            "data": contains_exactly(
                                contains_exactly(13, 12),
                                "some_value",
                                has_entries({"nested_data": "nested_data_value"}),
                            ),
                            "time": "now",
                        }
                    ),
                }
            ),
        )

    def test_load_item_multiple_request_attribute(self):
        """Tests database item loading for  a model with
        attributes that require multiple requests nested in dicts and lists.
        """
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "foo": self.attribute_mocks[0],
                "nested": {"bar": self.attribute_mocks[1]},
            },
        )
        self.item_mapper.load.return_value = {}
        self.attribute_mocks[0].load.return_value = "foo_value"
        self.attribute_mocks[1].load.return_value = ["bar_value_1", "bar_value_2"]

        item = database_item.load(
            self.base_response,
            {
                "foo": {
                    "request1": self.attribute_responses[0],
                    "request2": self.attribute_responses[1],
                },
                "nested": {
                    "bar": [
                        self.attribute_responses[2],
                        {
                            "req1": self.attribute_responses[3],
                            "req2": self.attribute_responses[4],
                        },
                    ]
                },
            },
        )

        assert_that(
            self.item_mapper.load.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(self.base_response))),
        )

        for attribute, response in zip(
            self.attribute_mocks[:2],
            [
                has_entries(
                    {
                        "request1": self.attribute_responses[0],
                        "request2": self.attribute_responses[1],
                    }
                ),
                contains_exactly(
                    self.attribute_responses[2],
                    has_entries(
                        {
                            "req1": self.attribute_responses[3],
                            "req2": self.attribute_responses[4],
                        }
                    ),
                ),
            ],
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    has_properties(args=contains_exactly(self.base_response, response))
                ),
            )

        assert_that(
            item,
            has_entries(
                {
                    "foo": "foo_value",
                    "nested": has_entries(
                        {"bar": contains_exactly("bar_value_1", "bar_value_2")}
                    ),
                },
            ),
        )

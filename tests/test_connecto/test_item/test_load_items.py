"""DatabaseItem load items tests"""

import unittest
from unittest.mock import MagicMock

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.wrap_matcher import wrap_matcher


from hamcrest import (
    assert_that,
    contains_exactly,
    has_entries,
    has_properties,
    all_of,
    instance_of,
    empty,
    none,
    contains_inanyorder,
)

from connecto.item import DatabaseItem
from connecto.attribute import DatabaseAttribute
from connecto.mapper import ItemMapper


def _mock_select_response(_id, base_response, attribute_response):
    return base_response, attribute_response.values[_id]


class ReturnsWhenCalled(BaseMatcher):
    """Implementation of the returns_when_called matcher."""

    def __init__(self, matcher):
        self.matcher = wrap_matcher(matcher)

    def _matches(self, item):
        return self.matcher.matches(item())

    def describe_to(self, description):
        description.append_text("Return value matching ")
        self.matcher.describe_to(description)


def returns_when_called(matcher):
    """Matches if the return value of the operand called without argument
    matches the specified matcher.
    """
    return ReturnsWhenCalled(matcher)


class TestDatabaseItemLoadItems(unittest.TestCase):
    # pylint: disable=R0801

    """Tests items loading depending on the complexity of the model."""

    def setUp(self):
        self.base_response = MagicMock(name="mock base response")
        self.item_mapper = MagicMock(spec=ItemMapper)

        self.attribute_responses = [
            MagicMock(
                values=[
                    MagicMock(name=f"mock response for attribute {j} of item {i}")
                    for i in range(3)
                ],
                name=f"mock response for attribute {j}",
            )
            for j in range(6)
        ]
        self.attribute_mocks = [
            MagicMock(spec=DatabaseAttribute, responses=self.attribute_responses[i])
            for i in range(6)
        ]

        self.item_mapper.select_response.side_effect = _mock_select_response

    def test_load_items_single_attribute_model(self):
        """Tests database item loading for a single attribute model."""
        database_item = DatabaseItem(self.item_mapper, self.attribute_mocks[0])

        self.attribute_mocks[0].load.side_effect = ["John Doe", "pipo", "molo"]

        self.item_mapper.load_items.return_value = [(i, MagicMock()) for i in range(3)]
        # Real call to the method under test
        items = database_item.load_items(
            self.base_response, self.attribute_responses[0]
        )

        assert_that(
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        returns_when_called(none()), self.base_response
                    )
                )
            ),
        )

        assert_that(
            self.attribute_mocks[0].load.call_args_list,
            contains_exactly(
                *[
                    has_properties(
                        args=contains_exactly(
                            self.base_response, self.attribute_responses[0].values[i]
                        )
                    )
                    for i in range(3)
                ]
            ),
        )

        assert_that(
            items,
            contains_inanyorder(
                (0, "John Doe"),
                (1, "pipo"),
                (2, "molo"),
            ),
        )

    def _test_load_items_simple_tuple_or_list_model(self, collection_type):
        database_item = DatabaseItem(
            self.item_mapper, collection_type(self.attribute_mocks[:3])
        )

        self.item_mapper.load_items.return_value = [
            (0, []),
            (1, []),
            (2, []),
        ]
        self.attribute_mocks[0].load.side_effect = ["jdoe", "pipo", "molo"]
        self.attribute_mocks[1].load.side_effect = ["John Doe", "Pipo", "Molo"]
        self.attribute_mocks[2].load.side_effect = [
            [
                "mail1@example.org",
                "mail2@jdoe.fr",
            ],
            ["pipo@example.org"],
            ["molo@pipo.fr"],
        ]

        # Real call to the method under test
        items = database_item.load_items(
            self.base_response, self.attribute_responses[:3]
        )

        assert_that(
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        returns_when_called(all_of(instance_of(list), empty())),
                        self.base_response,
                    )
                )
            ),
        )

        for attribute, response in zip(
            self.attribute_mocks[:3], self.attribute_responses[:3]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    *[
                        has_properties(
                            args=contains_exactly(
                                self.base_response, response.values[i]
                            )
                        )
                        for i in range(3)
                    ]
                ),
            )

        assert_that(
            items,
            contains_inanyorder(
                contains_exactly(
                    0,
                    all_of(
                        instance_of(collection_type),
                        contains_exactly(
                            "jdoe",
                            "John Doe",
                            contains_exactly("mail1@example.org", "mail2@jdoe.fr"),
                        ),
                    ),
                ),
                contains_exactly(
                    1,
                    all_of(
                        instance_of(collection_type),
                        contains_exactly(
                            "pipo",
                            "Pipo",
                            contains_exactly("pipo@example.org"),
                        ),
                    ),
                ),
                contains_exactly(
                    2,
                    all_of(
                        instance_of(collection_type),
                        contains_exactly(
                            "molo",
                            "Molo",
                            contains_exactly("molo@pipo.fr"),
                        ),
                    ),
                ),
            ),
        )

    def test_load_items_simple_tuple_model(self):
        """Tests loading of multiple items for a tuple model."""
        self._test_load_items_simple_tuple_or_list_model(tuple)

    def test_load_items_simple_list_model(self):
        """Tests loading of multiple items for a list model."""
        self._test_load_items_simple_tuple_or_list_model(list)

    def test_load_items_simple_dict_model(self):
        """Tests loading of multiple items for a dict model."""
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "login": self.attribute_mocks[0],
                "name": self.attribute_mocks[1],
                "contact": self.attribute_mocks[2],
            },
        )

        self.item_mapper.load_items.return_value = [
            (0, {}),
            (1, {}),
            (2, {}),
        ]
        self.attribute_mocks[0].load.side_effect = ["jdoe", "pipo", "molo"]
        self.attribute_mocks[1].load.side_effect = ["John Doe", "Pipo", "Molo"]
        self.attribute_mocks[2].load.side_effect = [
            [
                "mail1@example.org",
                "mail2@jdoe.fr",
            ],
            ["pipo@example.org"],
            ["molo@pipo.fr"],
        ]

        # Real call to the method under test
        items = database_item.load_items(
            self.base_response,
            {
                "login": self.attribute_responses[0],
                "name": self.attribute_responses[1],
                "contact": self.attribute_responses[2],
            },
        )

        assert_that(
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(returns_when_called({}), self.base_response)
                )
            ),
        )

        for attribute, response in zip(
            self.attribute_mocks[:3], self.attribute_responses[:3]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    *[
                        has_properties(
                            args=contains_exactly(
                                self.base_response, response.values[i]
                            )
                        )
                        for i in range(3)
                    ]
                ),
            )

        assert_that(
            items,
            contains_inanyorder(
                contains_exactly(
                    0,
                    has_entries(
                        {
                            "login": "jdoe",
                            "name": "John Doe",
                            "contact": contains_exactly(
                                "mail1@example.org", "mail2@jdoe.fr"
                            ),
                        }
                    ),
                ),
                contains_exactly(
                    1,
                    has_entries(
                        {
                            "login": "pipo",
                            "name": "Pipo",
                            "contact": contains_exactly("pipo@example.org"),
                        }
                    ),
                ),
                contains_exactly(
                    2,
                    has_entries(
                        {
                            "login": "molo",
                            "name": "Molo",
                            "contact": contains_exactly("molo@pipo.fr"),
                        }
                    ),
                ),
            ),
        )

    def test_load_items_with_complex_nested_attributes(self):
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

        self.item_mapper.load_items.return_value = [(i, {}) for i in range(3)]
        self.attribute_mocks[0].load.side_effect = ["jdoe", "pipo", "molo"]
        self.attribute_mocks[1].load.side_effect = [13, 6, "AC"]
        self.attribute_mocks[2].load.side_effect = [
            12,
            7,
            "AB",
        ]
        self.attribute_mocks[3].load.side_effect = [
            "some_value",
            "other_value",
            "awesome_value",
        ]
        self.attribute_mocks[4].load.side_effect = ["tic", "tac", "toe"]
        self.attribute_mocks[5].load.side_effect = ["now", "after", "before"]

        # Real call to the method under test
        items = database_item.load_items(
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
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(returns_when_called({}), self.base_response)
                )
            ),
        )

        for attribute, response in zip(self.attribute_mocks, self.attribute_responses):
            assert_that(
                attribute.load.call_args_list,
                contains_exactly(
                    *[
                        has_properties(
                            args=contains_exactly(
                                self.base_response, response.values[i]
                            )
                        )
                        for i in range(3)
                    ]
                ),
            )

        assert_that(
            items,
            contains_inanyorder(
                contains_exactly(
                    0,
                    has_entries(
                        {
                            "name": "jdoe",
                            "nested": has_entries(
                                {
                                    "data": contains_exactly(
                                        contains_exactly(13, 12),
                                        "some_value",
                                        has_entries({"nested_data": "tic"}),
                                    ),
                                    "time": "now",
                                }
                            ),
                        }
                    ),
                ),
                contains_exactly(
                    1,
                    has_entries(
                        {
                            "name": "pipo",
                            "nested": has_entries(
                                {
                                    "data": contains_exactly(
                                        contains_exactly(6, 7),
                                        "other_value",
                                        has_entries({"nested_data": "tac"}),
                                    ),
                                    "time": "after",
                                }
                            ),
                        }
                    ),
                ),
                contains_exactly(
                    2,
                    has_entries(
                        {
                            "name": "molo",
                            "nested": has_entries(
                                {
                                    "data": contains_exactly(
                                        contains_exactly("AC", "AB"),
                                        "awesome_value",
                                        has_entries({"nested_data": "toe"}),
                                    ),
                                    "time": "before",
                                }
                            ),
                        }
                    ),
                ),
            ),
        )

    def test_load_items_multiple_request_attribute(self):
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
        self.item_mapper.load_items.return_value = [
            (0, {}),
            (1, {}),
            (2, {}),
        ]
        self.attribute_mocks[0].load.side_effect = ["foo", "bar", "baz"]
        self.attribute_mocks[1].load.side_effect = [
            ["foo_value_1", "foo_value_2"],
            ["bar_value_1", "bar_value_2"],
            ["baz_value_1", "baz_value_2"],
        ]

        items = database_item.load_items(
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
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(returns_when_called({}), self.base_response)
                )
            ),
        )

        assert_that(
            self.attribute_mocks[0].load.call_args_list,
            contains_exactly(
                *[
                    has_properties(
                        args=contains_exactly(
                            self.base_response,
                            has_entries(
                                {
                                    "request1": self.attribute_responses[0].values[i],
                                    "request2": self.attribute_responses[1].values[i],
                                }
                            ),
                        )
                    )
                    for i in range(3)
                ]
            ),
        )
        assert_that(
            self.attribute_mocks[1].load.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(
                        args=contains_exactly(
                            self.base_response,
                            contains_exactly(
                                self.attribute_responses[2].values[i],
                                has_entries(
                                    {
                                        "req1": self.attribute_responses[3].values[i],
                                        "req2": self.attribute_responses[4].values[i],
                                    }
                                ),
                            ),
                        )
                    )
                    for i in range(3)
                ]
            ),
        )

        assert_that(
            items,
            contains_inanyorder(
                contains_exactly(
                    0,
                    has_entries(
                        {
                            "foo": "foo",
                            "nested": has_entries(
                                {"bar": contains_exactly("foo_value_1", "foo_value_2")}
                            ),
                        },
                    ),
                ),
                contains_exactly(
                    1,
                    has_entries(
                        {
                            "foo": "bar",
                            "nested": has_entries(
                                {"bar": contains_exactly("bar_value_1", "bar_value_2")}
                            ),
                        },
                    ),
                ),
                contains_exactly(
                    2,
                    has_entries(
                        {
                            "foo": "baz",
                            "nested": has_entries(
                                {"bar": contains_exactly("baz_value_1", "baz_value_2")}
                            ),
                        },
                    ),
                ),
            ),
        )

    def _test_load_simple_tuple_or_list_model_with_constants(self, collection_type):
        database_item = DatabaseItem(
            self.item_mapper,
            collection_type(
                [self.attribute_mocks[0], "constant", self.attribute_mocks[1]]
            ),
        )

        self.item_mapper.load_items.return_value = [
            (0, []),
            (1, []),
            (2, []),
        ]
        self.attribute_mocks[0].load.side_effect = ["jdoe", "pipo", "molo"]
        self.attribute_mocks[1].load.side_effect = [
            [
                "mail1@example.org",
                "mail2@jdoe.fr",
            ],
            ["pipo@example.org"],
            ["molo@pipo.fr"],
        ]

        # Real call to the method under test
        items = database_item.load_items(
            self.base_response, self.attribute_responses[:2]
        )

        assert_that(
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(returns_when_called([]), self.base_response)
                )
            ),
        )

        for attribute, response in zip(
            self.attribute_mocks[:2], self.attribute_responses[:2]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_inanyorder(
                    *[
                        has_properties(
                            args=contains_exactly(
                                self.base_response, response.values[i]
                            )
                        )
                        for i in range(3)
                    ]
                ),
            )

        assert_that(
            items,
            contains_inanyorder(
                contains_exactly(
                    0,
                    all_of(
                        instance_of(collection_type),
                        contains_exactly(
                            "jdoe",
                            "constant",
                            contains_exactly("mail1@example.org", "mail2@jdoe.fr"),
                        ),
                    ),
                ),
                contains_exactly(
                    1,
                    all_of(
                        instance_of(collection_type),
                        contains_exactly(
                            "pipo",
                            "constant",
                            contains_exactly("pipo@example.org"),
                        ),
                    ),
                ),
                contains_exactly(
                    2,
                    all_of(
                        instance_of(collection_type),
                        contains_exactly(
                            "molo",
                            "constant",
                            contains_exactly("molo@pipo.fr"),
                        ),
                    ),
                ),
            ),
        )

    def test_load_simple_tuple_model_with_constants(self):
        """Tests database item loading for a tuple model with constants."""
        self._test_load_simple_tuple_or_list_model_with_constants(tuple)

    def test_load_simple_list_model_with_constants(self):
        """Tests database item loading for a list model with constants."""
        self._test_load_simple_tuple_or_list_model_with_constants(list)

    def test_load_simple_dict_model_with_constants(self):
        """Tests database item loading for a dict model with constants."""
        database_item = DatabaseItem(
            self.item_mapper,
            {
                "login": self.attribute_mocks[0],
                "name": "John Doe",
                "contact": self.attribute_mocks[1],
            },
        )

        self.item_mapper.load_items.return_value = [
            (0, {}),
            (1, {}),
            (2, {}),
        ]
        self.attribute_mocks[0].load.side_effect = ["jdoe", "pipo", "molo"]
        self.attribute_mocks[1].load.side_effect = [
            [
                "mail1@example.org",
                "mail2@jdoe.fr",
            ],
            ["pipo@example.org"],
            ["molo@pipo.fr"],
        ]

        # Real call to the method under test
        items = database_item.load_items(
            self.base_response,
            {
                "login": self.attribute_responses[0],
                "contact": self.attribute_responses[1],
            },
        )

        assert_that(
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(returns_when_called({}), self.base_response)
                )
            ),
        )

        for attribute, response in zip(
            self.attribute_mocks[:2], self.attribute_responses[:2]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_inanyorder(
                    *[
                        has_properties(
                            args=contains_exactly(
                                self.base_response, response.values[i]
                            )
                        )
                        for i in range(3)
                    ]
                ),
            )

        assert_that(
            items,
            contains_inanyorder(
                contains_exactly(
                    0,
                    has_entries(
                        {
                            "login": "jdoe",
                            "name": "John Doe",
                            "contact": contains_exactly(
                                "mail1@example.org", "mail2@jdoe.fr"
                            ),
                        }
                    ),
                ),
                contains_exactly(
                    1,
                    has_entries(
                        {
                            "login": "pipo",
                            "name": "John Doe",
                            "contact": contains_exactly("pipo@example.org"),
                        }
                    ),
                ),
                contains_exactly(
                    2,
                    has_entries(
                        {
                            "login": "molo",
                            "name": "John Doe",
                            "contact": contains_exactly("molo@pipo.fr"),
                        }
                    ),
                ),
            ),
        )

    def test_load_item_with_complex_nested_attributes_and_constants(self):
        """Tests database item loading for a model with attributes and constants nested in
        dicts, lists and tuples.
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

        self.item_mapper.load_items.return_value = [(i, {}) for i in range(3)]
        self.attribute_mocks[0].load.side_effect = ["jdoe", "pipo", "molo"]
        self.attribute_mocks[1].load.side_effect = [13, 6, "AC"]
        self.attribute_mocks[2].load.side_effect = [
            12,
            7,
            "AB",
        ]
        self.attribute_mocks[3].load.side_effect = ["tic", "tac", "toe"]

        # Real call to the method under test
        items = database_item.load_items(
            self.base_response,
            {
                "name": self.attribute_responses[0],
                "nested": {
                    "data": [
                        [self.attribute_responses[1], self.attribute_responses[2]],
                        {"nested_data": self.attribute_responses[3]},
                    ],
                },
            },
        )

        assert_that(
            self.item_mapper.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(returns_when_called({}), self.base_response)
                )
            ),
        )

        for attribute, response in zip(
            self.attribute_mocks[:4], self.attribute_responses[:4]
        ):
            assert_that(
                attribute.load.call_args_list,
                contains_inanyorder(
                    *[
                        has_properties(
                            args=contains_exactly(
                                self.base_response, response.values[i]
                            )
                        )
                        for i in range(3)
                    ]
                ),
            )

        assert_that(
            items,
            contains_inanyorder(
                contains_exactly(
                    0,
                    has_entries(
                        {
                            "name": "jdoe",
                            "nested": has_entries(
                                {
                                    "data": contains_exactly(
                                        contains_exactly(13, 12),
                                        "constant",
                                        has_entries({"nested_data": "tic"}),
                                    ),
                                    "time": "now",
                                }
                            ),
                        }
                    ),
                ),
                contains_exactly(
                    1,
                    has_entries(
                        {
                            "name": "pipo",
                            "nested": has_entries(
                                {
                                    "data": contains_exactly(
                                        contains_exactly(6, 7),
                                        "constant",
                                        has_entries({"nested_data": "tac"}),
                                    ),
                                    "time": "now",
                                }
                            ),
                        }
                    ),
                ),
                contains_exactly(
                    2,
                    has_entries(
                        {
                            "name": "molo",
                            "nested": has_entries(
                                {
                                    "data": contains_exactly(
                                        contains_exactly("AC", "AB"),
                                        "constant",
                                        has_entries({"nested_data": "toe"}),
                                    ),
                                    "time": "now",
                                }
                            ),
                        }
                    ),
                ),
            ),
        )

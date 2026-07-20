"""DatabaseItem filter compilation tests"""

import unittest
from unittest.mock import MagicMock

from hamcrest import (
    assert_that,
    contains_exactly,
    has_properties,
    equal_to,
)

from stricto.filter import SFilter, Operator

from connecto.item import DatabaseItem
from connecto.item_filter import ItemFilterCompiler, AttributeFilterCompiler
from connecto.mapper import ItemMapper


def mock_select_and(conditions):
    """Fake implementation of an AND operation.
    """
    return f"({" AND ".join(conditions)})"


def mock_select_or(conditions):
    """Fake implementation of an OR operation.
    """
    return f"({" OR ".join(conditions)})"


class TestDatabaseItemSelectFilter(unittest.TestCase):
    """Test filter compilation for a DatabaseItem.

    Most of the tested features are actually implemented in connecto.item_filter
    so this is a kind of integration test for the database_item.select_filter()
    method.
    """

    def setUp(self):
        self.item_filter_compiler = MagicMock(spec=ItemFilterCompiler)

        self.attribute_mocks = [MagicMock(spec=AttributeFilterCompiler) for i in range(6)]

        # Not supposed to be required but prevents some Pylint warnings
        self.item_filter_compiler.select_and = MagicMock()
        self.item_filter_compiler.select_or = MagicMock()

    def test_select_filter_single_attribute_model(self):
        """Tests select_filter() for a single attribute model.

        This is a generic call test.
        """
        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            self.attribute_mocks[0],
            # No need for filter compiler since filters are only applied to
            # explicit attributes of the model, without AND or OR
        )

        item_filter = SFilter("$", Operator.EQ, "mock_id")
        select_filter = database_item.select_filter(item_filter)

        assert_that(
            self.attribute_mocks[0].select_eq.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )

        assert_that(
            select_filter,
            equal_to(self.attribute_mocks[0].select_eq.return_value),
        )

    def test_select_filter_compile_single_attribute_model(self):
        """Tests select_filter() for a single attribute model.

        Checks the result of a filter compiled as a string using fake
        implementations of each operation.
        """
        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            self.attribute_mocks[0],
            # No need for filter compiler since filters are only applied to
            # explicit attributes of the model, without AND or OR
        )

        self.attribute_mocks[0].select_eq.return_value = "field == mock_id"

        item_filter = SFilter("$", Operator.EQ, "mock_id")
        select_filter = database_item.select_filter(item_filter)

        assert_that(select_filter, equal_to("field == mock_id"))

    def _test_select_request_simple_list_or_tuple_model(self, collection_type):
        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            collection_type(self.attribute_mocks),
            self.item_filter_compiler,
        )

        item_filter = SFilter(
            "$",
            Operator.AND,
            [
                SFilter("[0]", Operator.EQ, "data"),
                # No filter for item 1
                SFilter("[2]", Operator.GT, 12),
                # No filter for other items
            ],
        )
        select_filter = database_item.select_filter(item_filter)

        assert_that(
            self.item_filter_compiler.select_and.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        contains_exactly(
                            self.attribute_mocks[0].select_eq.return_value,
                            self.attribute_mocks[2].select_gt.return_value,
                        )
                    )
                )
            ),
        )

        assert_that(
            self.attribute_mocks[0].select_eq.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("data"))),
        )

        assert_that(
            self.attribute_mocks[2].select_gt.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(12))),
        )

        assert_that(
            select_filter,
            equal_to(
                self.item_filter_compiler.select_and.return_value,
            ),
        )

    def test_select_request_simple_tuple_model(self):
        """Tests select_filter() for a tuple model.

        This is a generic call test.
        """
        self._test_select_request_simple_list_or_tuple_model(tuple)

    def test_select_request_simple_list_model(self):
        """Tests select_filter() for a list model.

        This is a generic call test.
        """
        self._test_select_request_simple_list_or_tuple_model(list)

    def _test_select_request_compile_simple_list_or_tuple_model(self, collection_type):
        self.item_filter_compiler.select_and.side_effect = mock_select_and

        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            collection_type(self.attribute_mocks),
            self.item_filter_compiler,
        )

        self.attribute_mocks[0].select_eq.return_value = 'field1 == "data"'
        self.attribute_mocks[2].select_gt.return_value = "field2 > 12"

        item_filter = SFilter(
            "$",
            Operator.AND,
            [
                SFilter("[0]", Operator.EQ, "data"),
                # No filter for item 1
                SFilter("[2]", Operator.GT, 12),
                # No filter for other items
            ],
        )
        select_filter = database_item.select_filter(item_filter)

        assert_that(
            select_filter,
            equal_to('(field1 == "data" AND field2 > 12)'),
        )

    def test_select_request_compile_simple_tuple_model(self):
        """Tests select_filter() for a tuple model.

        Checks the result of a filter compiled as a string using fake
        implementations of each operation.
        """
        self._test_select_request_compile_simple_list_or_tuple_model(tuple)

    def test_select_request_compile_simple_list_model(self):
        """Tests select_filter() for a list model.

        Checks the result of a filter compiled as a string using fake
        implementations of each operation.
        """
        self._test_select_request_compile_simple_list_or_tuple_model(list)

    def test_select_filter_simple_dict_model(self):
        """Tests select_filter() for a dict model.

        This is a generic call test.
        """
        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            {
                "login": self.attribute_mocks[0],
                "name": self.attribute_mocks[1],
                "contact": self.attribute_mocks[2],
            },
            item_filter_compiler=self.item_filter_compiler,
        )

        item_filter = SFilter(
            "$",
            Operator.AND,
            [
                # No need to specify a filter for each field
                SFilter("login", Operator.EQ, "mock_login"),
                SFilter("name", Operator.REG, "mock.*"),
                # Value not included in the model: must be processed by the item
                # mapper
                SFilter("foo", Operator.LTE, 666),
            ],
        )

        select_filter = database_item.select_filter(item_filter)

        assert_that(
            self.item_filter_compiler.select_and.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        contains_exactly(
                            self.attribute_mocks[0].select_eq.return_value,
                            self.attribute_mocks[1].select_reg.return_value,
                            self.item_filter_compiler.select_lte.return_value,
                        )
                    )
                )
            ),
        )
        assert_that(
            self.attribute_mocks[0].select_eq.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_login"))),
        )
        assert_that(
            self.attribute_mocks[1].select_reg.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock.*"))),
        )
        assert_that(
            self.item_filter_compiler.select_lte.call_args_list,
            contains_exactly(
                has_properties(args=contains_exactly(contains_exactly("foo"), 666))
            ),
        )
        assert_that(
            select_filter,
            equal_to(
                # Compiled root instruction
                self.item_filter_compiler.select_and.return_value,
            ),
        )

    def test_select_filter_compile_simple_dict_model(self):
        """Tests select_filter() for a dict model.

        Checks the result of a filter compiled as a string using fake
        implementations of each operation.
        """
        self.item_filter_compiler.select_and.side_effect = mock_select_and
        self.item_filter_compiler.select_or.side_effect = mock_select_or

        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            {
                "login": self.attribute_mocks[0],
                "name": self.attribute_mocks[1],
                "contact": self.attribute_mocks[2],
            },
            item_filter_compiler=self.item_filter_compiler,
        )

        item_filter = SFilter(
            "$",
            Operator.AND,
            [
                # No need to specify a filter for each field
                SFilter("login", Operator.EQ, "mock_login"),
                SFilter("name", Operator.REG, "mock.*"),
                # Value not included in the model: must be processed by the item
                # mapper
                SFilter("foo", Operator.LTE, 666),
            ],
        )
        self.attribute_mocks[0].select_eq.return_value = "login == mock_login"
        self.attribute_mocks[1].select_reg.return_value = "match(name, mock.*)"
        self.item_filter_compiler.select_lte.return_value = "foo >= 666"

        select_filter = database_item.select_filter(item_filter)

        assert_that(
            select_filter,
            equal_to("(login == mock_login AND match(name, mock.*) AND foo >= 666)"),
        )

    def test_select_filter_with_complex_nested_attributes(self):
        """Tests select_filter() for a dict model with nested structures.

        This is a generic call test.
        """
        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            {
                "name": self.attribute_mocks[0],
                "nested": {
                    "data": [
                        [self.attribute_mocks[1], self.attribute_mocks[2]],
                        self.attribute_mocks[3],
                        {"nested_data": self.attribute_mocks[4]},
                    ],
                    "time": self.attribute_mocks[5],
                },
            },
            item_filter_compiler=self.item_filter_compiler,
        )

        item_filter = SFilter(
            "$",
            Operator.AND,
            [
                SFilter("name", Operator.REG, "toto.*"),
                SFilter(
                    "nested",
                    Operator.OR,
                    [
                        SFilter("data[0][0]", Operator.GT, 13),
                        SFilter("data[0][0]", Operator.LT, 14),
                        SFilter("data[0][1]", Operator.EQ, 12),
                        # Attribute not included in the model: processed by item
                        # mapper
                        SFilter("foo", Operator.GTE, 44),
                        SFilter(
                            "data[1]",
                            Operator.AND,
                            [
                                SFilter("$", Operator.REG, r"\S*"),
                                SFilter("$", Operator.EQ, "bar"),
                            ],
                        ),
                        SFilter("time", Operator.LT, 2027),
                    ],
                ),
            ],
        )

        select_filter = database_item.select_filter(item_filter)

        assert_that(
            self.item_filter_compiler.select_and.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        contains_exactly(
                            self.attribute_mocks[3].select_reg.return_value,
                            self.attribute_mocks[3].select_eq.return_value,
                        )
                    )
                ),
                has_properties(
                    args=contains_exactly(
                        contains_exactly(
                            self.attribute_mocks[0].select_reg.return_value,
                            self.item_filter_compiler.select_or.return_value,
                        ),
                    )
                ),
            ),
        )
        assert_that(
            self.item_filter_compiler.select_or.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        contains_exactly(
                            self.attribute_mocks[1].select_gt.return_value,
                            self.attribute_mocks[1].select_lt.return_value,
                            self.attribute_mocks[2].select_eq.return_value,
                            self.item_filter_compiler.select_gte.return_value,
                            self.item_filter_compiler.select_and.return_value,
                            self.attribute_mocks[5].select_lt.return_value,
                        )
                    )
                )
            ),
        )
        assert_that(
            self.attribute_mocks[0].select_reg.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("toto.*"))),
        )
        assert_that(
            self.attribute_mocks[1].select_gt.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(13))),
        )
        assert_that(
            self.attribute_mocks[1].select_lt.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(14))),
        )
        assert_that(
            self.attribute_mocks[2].select_eq.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(12))),
        )
        assert_that(
            self.item_filter_compiler.select_gte.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(contains_exactly("nested", "foo"), 44)
                )
            ),
        )
        assert_that(
            self.attribute_mocks[3].select_reg.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(r"\S*"))),
        )
        assert_that(
            self.attribute_mocks[5].select_lt.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(2027))),
        )

        assert_that(
            select_filter,
            equal_to(
                self.item_filter_compiler.select_and.return_value,
            ),
        )

    def test_select_filter_compile_model_with_complex_nested_attributes(self):
        """Tests select_filter() for a dict model with nested structures.

        Checks the result of a filter compiled as a string using fake
        implementations of each operation.
        """
        self.item_filter_compiler.select_and = mock_select_and
        self.item_filter_compiler.select_or = mock_select_or

        database_item = DatabaseItem(
            MagicMock(spec=ItemMapper),
            {
                "name": self.attribute_mocks[0],
                "nested": {
                    "data": [
                        [self.attribute_mocks[1], self.attribute_mocks[2]],
                        self.attribute_mocks[3],
                        {"nested_data": self.attribute_mocks[4]},
                    ],
                    "time": self.attribute_mocks[5],
                },
            },
            item_filter_compiler=self.item_filter_compiler,
        )

        self.attribute_mocks[0].select_reg.return_value = 'match(name, "toto.*")'
        self.attribute_mocks[1].select_gt.return_value = "attr1 > 13"
        self.attribute_mocks[1].select_lt.return_value = "attr1 < 14"
        self.attribute_mocks[2].select_eq.return_value = "attr2 == 12"
        self.item_filter_compiler.select_gte.return_value = "nested.foo >= 44"
        self.attribute_mocks[3].select_reg.return_value = 'match(attr4, "\\S*")'
        self.attribute_mocks[3].select_eq.return_value = 'attr4 == "bar"'
        self.attribute_mocks[5].select_lt.return_value = "time < 2027"

        item_filter = SFilter(
            "$",
            Operator.AND,
            [
                SFilter("name", Operator.REG, "toto.*"),
                SFilter(
                    "nested",
                    Operator.OR,
                    [
                        SFilter("data[0][0]", Operator.GT, 13),
                        SFilter("data[0][0]", Operator.LT, 14),
                        SFilter("data[0][1]", Operator.EQ, 12),
                        # Attribute not included in the model: processed by item
                        # mapper
                        SFilter("foo", Operator.GTE, 44),
                        SFilter(
                            "data[1]",
                            Operator.AND,
                            [
                                SFilter("$", Operator.REG, r"\S*"),
                                SFilter("$", Operator.EQ, "bar"),
                            ],
                        ),
                        SFilter("time", Operator.LT, 2027),
                    ],
                ),
            ],
        )

        select_filter = database_item.select_filter(item_filter)

        assert_that(
            select_filter,
            equal_to(
                '(match(name, "toto.*") AND '
                "(attr1 > 13 OR attr1 < 14 OR "
                "attr2 == 12 OR nested.foo >= 44 OR "
                '(match(attr4, "\\S*") AND attr4 == "bar") OR time < 2027'
                "))"
            ),
        )

"""Test module for DatabaseEngine select operation."""

from unittest.mock import patch, MagicMock

from hamcrest import (
    assert_that,
    contains_exactly,
    has_properties,
    has_entries,
    contains_inanyorder,
    equal_to,
)

from stricto import SFilter

from connecto.engine import DatabaseEngine

from .operation_test_case import OperationTestCase, mock_execute_request


@patch("connecto.item.DatabaseItem", autospec=True)
class TestDatabaseEngineSelect(OperationTestCase):
    """Tests the select operation of the DatabaseEngine."""

    def setUp(self):
        super().setUp()
        self.default_connection.execute_select.side_effect = mock_execute_request
        self.custom_connection.execute_select.side_effect = mock_execute_request

    def test_select_single_attribute(self, database_item):
        """Tests method DatabaseEngine.select for an existing item with a single
        item as attribute select request.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.select_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[4],
        )

        item_filter = MagicMock(spec=SFilter)
        # Real call to the method under test
        items = engine.select(item_filter)

        assert_that(
            database_item.return_value.select_filter.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(item_filter))),
        )

        assert_that(
            database_item.return_value.select_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        database_item.return_value.select_filter.return_value
                    )
                )
            ),
        )

        # Ensure select was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_select.call_args_list,
            contains_inanyorder(
                has_properties(args=contains_exactly(self.mock_requests[0]))
            ),
        )
        assert_that(
            self.custom_connection.execute_select.call_args_list,
            contains_exactly(
                has_properties(args=contains_exactly(self.mock_requests[4]))
            ),
        )

        # pylint: disable=R0801
        assert_that(
            database_item.return_value.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.mock_responses[0],
                        self.mock_responses[4],
                    ),
                )
            ),
        )
        # pylint: enable=R0801

        assert_that(items, equal_to(database_item.return_value.load_items.return_value))

    def test_select_list(self, database_item):
        """Tests method DatabaseEngine.select for an existing item with a list
        of attribute select requests.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.select_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[1:],
        )

        item_filter = MagicMock(spec=SFilter)
        # Real call to the method under test
        items = engine.select(item_filter)

        assert_that(
            database_item.return_value.select_filter.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(item_filter))),
        )

        assert_that(
            database_item.return_value.select_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        database_item.return_value.select_filter.return_value
                    )
                )
            ),
        )

        # Ensure select was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_select.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )
        assert_that(
            self.custom_connection.execute_select.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

        # pylint: disable=R0801
        assert_that(
            database_item.return_value.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.mock_responses[0],
                        contains_exactly(*self.mock_responses[1:]),
                    ),
                )
            ),
        )
        # pylint: enable=R0801

        assert_that(items, equal_to(database_item.return_value.load_items.return_value))

    def test_select_dict(self, database_item):
        """Tests method DatabaseEngine.select for an existing item with a
        dictionnary of nested structures as attribute select requests.
        """

        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        # pylint: disable=R0801
        database_item.return_value.select_request.return_value = (
            self.mock_requests[0],
            {
                "mock": self.mock_requests[1],
                "nested": {"item": self.mock_requests[2]},
                "list": [self.mock_requests[3], self.mock_requests[4]],
                "nested_list": [
                    [self.mock_requests[5], self.mock_requests[6]],
                    self.mock_requests[7],
                    {"nested_in_list": self.mock_requests[8]},
                ],
            },
        )
        # pylint: enable=R0801

        item_filter = MagicMock(spec=SFilter)
        # Real call to the method under test
        items = engine.select(item_filter)

        assert_that(
            database_item.return_value.select_filter.call_args_list,
            contains_exactly(has_properties(args=contains_exactly(item_filter))),
        )

        assert_that(
            database_item.return_value.select_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        database_item.return_value.select_filter.return_value
                    )
                )
            ),
        )

        # Ensure select was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_select.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )
        assert_that(
            self.custom_connection.execute_select.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

        # pylint: disable=R0801
        assert_that(
            database_item.return_value.load_items.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.mock_responses[0],
                        has_entries(
                            {
                                "mock": self.mock_responses[1],
                                "nested": has_entries({"item": self.mock_responses[2]}),
                                "list": contains_exactly(
                                    self.mock_responses[3], self.mock_responses[4]
                                ),
                                "nested_list": contains_exactly(
                                    contains_exactly(
                                        self.mock_responses[5], self.mock_responses[6]
                                    ),
                                    self.mock_responses[7],
                                    has_entries(
                                        {"nested_in_list": self.mock_responses[8]}
                                    ),
                                ),
                            }
                        ),
                    )
                )
            ),
        )
        # pylint: enable=R0801

        assert_that(items, equal_to(database_item.return_value.load_items.return_value))

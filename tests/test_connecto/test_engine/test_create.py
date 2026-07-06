"""
Test module for connecto.engine.py
"""

from unittest.mock import patch

from hamcrest import (
    assert_that,
    contains_exactly,
    has_properties,
    has_entries,
    contains_inanyorder,
    equal_to,
)

from connecto.engine import DatabaseEngine

from .operation_test_case import OperationTestCase, mock_execute_request


@patch("connecto.item.DatabaseItem", autospec=True)
class TestDatabaseEngineCreate(OperationTestCase):
    """Tests the search operation of the DatabaseEngine."""

    def setUp(self):
        super().setUp()
        self.default_connection.execute_create.side_effect = mock_execute_request
        self.custom_connection.execute_create.side_effect = mock_execute_request

    def test_create(self, database_item):
        """Tests method DatabaseEngine.create."""

        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.created_id.return_value = "unique_id_of_the_new_item"

        # pylint: disable=R0801
        database_item.return_value.create_request.return_value = (
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

        item_to_create = {"name": "new_item", "field": "some_value", "port": 1312}
        # Real call to the method under test
        item_id = engine.create(item_to_create)

        assert_that(
            database_item.return_value.create_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        # The call argument is checked using has_entries because it
                        # would be OK to pass a copy of the item_to_create as argument
                        has_entries(item_to_create)
                    )
                )
            ),
        )

        # Ensure create was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_create.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )
        assert_that(
            self.custom_connection.execute_create.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

        assert_that(
            database_item.return_value.created_id.call_args_list,
            contains_exactly(
                has_properties(args=contains_exactly(self.mock_responses[0]))
            ),
        )

        assert_that(item_id, equal_to("unique_id_of_the_new_item"))

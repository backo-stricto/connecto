"""Test module for DatabaseEngine delete operation."""

from unittest.mock import patch

from hamcrest import (
    assert_that,
    contains_exactly,
    has_properties,
    contains_inanyorder,
)

from connecto.engine import DatabaseEngine

from .operation_test_case import OperationTestCase, mock_execute_request


@patch("connecto.item.DatabaseItem", autospec=True)
class TestDatabaseEngineDelete(OperationTestCase):
    """Tests the delete operation of the DatabaseEngine."""

    def setUp(self):
        super().setUp()
        self.default_connection.execute_delete.side_effect = mock_execute_request
        self.custom_connection.execute_delete.side_effect = mock_execute_request

    def test_delete_single_attribute(self, database_item):
        """Tests method DatabaseEngine.delete for an existing item with a single
        item as attribute delete request.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.delete_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[4],
        )

        # Real call to the method under test
        engine.delete("mock_id")

        assert_that(
            database_item.return_value.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )

        # Ensure delete was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_delete.call_args_list, self.mock_requests[0]
        )

        assert_that(
            self.custom_connection.execute_delete.call_args_list, self.mock_requests[4]
        )

    def test_delete_list(self, database_item):
        """Tests method DatabaseEngine.delete for an existing item with a list
        of attribute delete requests.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.delete_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[1:],
        )

        # Real call to the method under test
        engine.delete("mock_id")

        assert_that(
            database_item.return_value.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )

        # Ensure delete was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_delete.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )

        assert_that(
            self.custom_connection.execute_delete.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

    def test_delete_dict(self, database_item):
        """Tests method DatabaseEngine.create for an existing item with a list
        of attribute create requests.
        """

        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        # pylint: disable=R0801
        database_item.return_value.delete_request.return_value = (
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

        # Real call to the method under test
        engine.delete("mock_id")

        assert_that(
            database_item.return_value.delete_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )

        # Ensure delete was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_delete.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )

        assert_that(
            self.custom_connection.execute_delete.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

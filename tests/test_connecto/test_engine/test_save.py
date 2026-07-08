"""Test module for DatabaseEngine save operation."""

from unittest.mock import patch, MagicMock

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
class TestDatabaseEngineSave(OperationTestCase):
    """Tests the save operation of the DatabaseEngine."""

    def setUp(self):
        super().setUp()
        self.default_connection.execute_update.side_effect = mock_execute_request
        self.custom_connection.execute_update.side_effect = mock_execute_request

    def test_save_single_attribute(self, database_item):
        """Tests method DatabaseEngine.save for an existing item with a single
        item as attribute update request.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.update_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[4],
        )

        updated_item = MagicMock()

        # Real call to the method under test
        engine.save("mock_id", updated_item)

        assert_that(
            database_item.return_value.update_request.call_args_list,
            contains_exactly(
                has_properties(args=contains_exactly("mock_id", equal_to(updated_item)))
            ),
        )

        # Ensure update was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_update.call_args_list, self.mock_requests[0]
        )
        assert_that(
            self.custom_connection.execute_update.call_args_list, self.mock_requests[4]
        )

    def test_save_list(self, database_item):
        """Tests method DatabaseEngine.save for an existing item with a list
        of attribute update requests.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.update_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[1:],
        )

        updated_item = [MagicMock() for _ in range(len(self.mock_requests[1:]))]

        # Real call to the method under test
        engine.save("mock_id", updated_item)

        assert_that(
            database_item.return_value.update_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly("mock_id", contains_exactly(*updated_item))
                )
            ),
        )

        # Ensure update was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_update.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )
        assert_that(
            self.custom_connection.execute_update.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

    def test_save_dict(self, database_item):
        """Tests method DatabaseEngine.save for an existing item with a
        dictionnary of nested structures as attribute update requests.
        """

        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        # pylint: disable=R0801
        database_item.return_value.update_request.return_value = (
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

        updated_item = {
            "name": "updated_item",
            "field": "up_to_date_value",
            "port": 1213,
        }

        # Real call to the method under test
        engine.save("mock_id", updated_item)

        assert_that(
            database_item.return_value.update_request.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly("mock_id", has_entries(updated_item))
                )
            ),
        )

        # Ensure update was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_update.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )
        assert_that(
            self.custom_connection.execute_update.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

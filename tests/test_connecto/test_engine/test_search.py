"""Test module for DatabaseEngine search operation."""

from unittest.mock import patch

from hamcrest import (
    assert_that,
    contains_exactly,
    has_properties,
    has_entries,
    contains_inanyorder,
    calling,
    raises,
    equal_to,
)

from connecto.engine import DatabaseEngine
from connecto.error import ItemNotFound

from .operation_test_case import OperationTestCase, mock_execute_request


@patch("connecto.item.DatabaseItem", autospec=True)
class TestDatabaseEngineSearch(OperationTestCase):
    """Tests the search operation of the DatabaseEngine."""

    def setUp(self):
        super().setUp()
        self.default_connection.execute_search.side_effect = mock_execute_request
        self.custom_connection.execute_search.side_effect = mock_execute_request

    def test_search_single_attribute(self, database_item):
        """Tests method DatabaseEngine.search for an existing item with a single
        item as attribute search request.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.search_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[4],
        )

        # Real call to the method under test
        _id, item = engine.search("mock_id")

        assert_that(
            database_item.return_value.search_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )

        # Ensure search was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_search.call_args_list,
            contains_inanyorder(
                has_properties(args=contains_exactly(self.mock_requests[0]))
            ),
        )
        assert_that(
            self.custom_connection.execute_search.call_args_list,
            contains_exactly(
                has_properties(args=contains_exactly(self.mock_requests[4]))
            ),
        )

        assert_that(
            database_item.return_value.load.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.mock_responses[0],
                        self.mock_responses[4],
                    ),
                )
            ),
        )

        assert_that(_id, equal_to("mock_id"))
        assert_that(item, equal_to(database_item.return_value.load.return_value))

    def test_search_list(self, database_item):
        """Tests method DatabaseEngine.search for an existing item with a list
        of attribute search requests.
        """
        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.search_request.return_value = (
            self.mock_requests[0],
            self.mock_requests[1:],
        )

        # Real call to the method under test
        _id, item = engine.search("mock_id")

        assert_that(
            database_item.return_value.search_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )

        # Ensure search was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_search.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )
        assert_that(
            self.custom_connection.execute_search.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

        assert_that(
            database_item.return_value.load.call_args_list,
            contains_exactly(
                has_properties(
                    args=contains_exactly(
                        self.mock_responses[0],
                        contains_exactly(*self.mock_responses[1:]),
                    ),
                )
            ),
        )

        assert_that(_id, equal_to("mock_id"))
        assert_that(item, equal_to(database_item.return_value.load.return_value))

    def test_search_dict(self, database_item):
        """Tests method DatabaseEngine.search for an existing item with a
        dictionnary of nested structures as attribute search requests.
        """

        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        # pylint: disable=R0801
        database_item.return_value.search_request.return_value = (
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
        _id, item = engine.search("mock_id")

        assert_that(
            database_item.return_value.search_request.call_args_list,
            contains_exactly(has_properties(args=contains_exactly("mock_id"))),
        )

        # Ensure search was called with appropriate parameters.
        assert_that(
            self.default_connection.execute_search.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[:4]
                ]
            ),
        )
        assert_that(
            self.custom_connection.execute_search.call_args_list,
            contains_inanyorder(
                *[
                    has_properties(args=contains_exactly(mock_request))
                    for mock_request in self.mock_requests[4:]
                ]
            ),
        )

        assert_that(
            database_item.return_value.load.call_args_list,
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

        assert_that(_id, equal_to("mock_id"))
        assert_that(item, equal_to(database_item.return_value.load.return_value))

    def test_search_not_found(self, database_item):
        """Tests DatabaseEngine.search method for an non existing item.

        Must raise a ItemNotFound.
        """

        engine = DatabaseEngine(self.default_connection, database_item.return_value)

        database_item.return_value.search_request.return_value = (
            self.mock_requests[0],
            {},
        )
        self.default_connection.execute_search.side_effect = ItemNotFound(
            "mock_id", "mocked database"
        )

        # Real call to the method under test
        assert_that(calling(engine.search).with_args("mock_id"), raises(ItemNotFound))

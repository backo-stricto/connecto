"""Test module for DatabaseEngine base features."""

import unittest

from unittest.mock import patch

from hamcrest import (
    assert_that,
    contains_exactly,
    has_properties,
)

from connecto.engine import DatabaseEngine


@patch("connecto.item.DatabaseItem", autospec=True)
@patch("connecto.connection.DatabaseConnection", autospec=True)
class TestDatabaseEngine(unittest.TestCase):
    """
    Test base features of the DatabaseEngine, that are not related to each
    operations.
    """

    def test_init_engine(self, connection, database_item):
        """Tests DatabaseEngine initialization. Ensures the database_item is
        properly initialized by the DatabaseEngine.
        """

        DatabaseEngine(connection.return_value, database_item.return_value)

        assert_that(
            database_item.return_value.set_default_connection.call_args_list,
            contains_exactly(
                has_properties(args=contains_exactly(connection.return_value))
            ),
        )

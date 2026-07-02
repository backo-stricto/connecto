"""
Test module for connecto.reverse_ref
"""

import unittest

from unittest.mock import MagicMock

from stricto.filter import Operator
from hamcrest import assert_that, equal_to, none, calling, raises

from connecto.connection import DatabaseConnection
from connecto.engine import DatabaseEngine
from connecto.item import DatabaseItem
from connecto.reverse_ref import ReverseRef, InvalidReverseRef
from connecto.mapper import ItemMapper
from connecto.attribute import DatabaseAttribute


class TestReverseRef(unittest.TestCase):
    """Tests ReverseRef resolution."""

    def setUp(self):
        self.connection = MagicMock(spec=DatabaseConnection)

        # Engine used to perform the select operation on the referenced items
        self.ref_engine = MagicMock(spec=DatabaseEngine)

        self.filter_item_mapper = MagicMock(spec=ItemMapper)
        # Init value of the loaded filter
        self.filter_item_mapper.load.return_value = []

        # Fake attribute that always returns the ID of the item, that is used to
        # check the "field" of the referenced item
        self.filter_attribute = MagicMock(spec=DatabaseAttribute, connection=None)
        self.filter_attribute.load.return_value = "mock_id"

        # A true filter that will be used to find the referenced item.
        # Because of the previous filter_attribute set up, the filter will be
        # loaded as ("$.field", Operator.EQ, "mock_id")
        item_filter = DatabaseItem(
            item_mapper=self.filter_item_mapper,
            model=("$.field", Operator.EQ, self.filter_attribute),
        )

        self.item_mapper = MagicMock(spec=ItemMapper)
        # Init value of the loaded item
        self.item_mapper.load.return_value = {}

        # True item under test, with a real ReverseRef
        self.item = DatabaseItem(
            item_mapper=self.item_mapper,
            model={"mock_ref": ReverseRef(self.ref_engine, item_filter)},
        )

        # Real engine that needs to resolve the ref
        self.engine = DatabaseEngine(self.connection, self.item)

    def test_reverse_ref(self):
        """Tests if a ReverseRef is resolved."""

        # Mock selected items among which the ref should be resolved
        self.ref_engine.select.return_value = (
            (0, {"field": "bip", "name": "foo"}),
            (1, {"field": "mock_id", "name": "bar"}),
            (2, {"field": "boop", "name": "baz"}),
        )

        _id, item = self.engine.search("mock_id")

        assert_that(item["mock_ref"], equal_to(1))

    def test_missing_reverse_ref(self):
        """Tests if a ReverseRef is resolved to None if no referenced item could
        be found."""

        # Mock selected items among which the ref should be resolved. No item
        # matches the reference.
        self.ref_engine.select.return_value = (
            (0, {"field": "bip", "name": "foo"}),
            (1, {"field": "bam", "name": "bar"}),
            (2, {"field": "boop", "name": "baz"}),
        )

        _id, item = self.engine.search("mock_id")

        assert_that(item["mock_ref"], none())

    def test_invalid_reverse_ref(self):
        """Tests if a ReverseRef raises an InvalidReverseRef if multiple items
        match the filter."""

        # Mock selected items among which the ref should be resolved. Multiple
        # items match the reference.
        self.ref_engine.select.return_value = (
            (0, {"field": "bip", "name": "foo"}),
            (1, {"field": "mock_id", "name": "bar"}),
            (2, {"field": "mock_id", "name": "baz"}),
        )

        assert_that(
            calling(self.engine.search).with_args("mock_id"), raises(InvalidReverseRef)
        )

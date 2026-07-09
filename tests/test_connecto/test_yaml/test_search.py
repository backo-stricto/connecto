"""
Module to test the search operation of the YAML connector.
"""

import unittest
import yaml

from hamcrest import (
    assert_that,
    equal_to,
    contains_inanyorder,
    has_entries,
    has_length,
    all_of,
    contains_exactly,
)

from tempfile import NamedTemporaryFile
from connecto.yaml import YamlEngine, YamlItem, MapByKey, YamlAttribute

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.hasmethod import hasmethod


class TestYamlSearch(unittest.TestCase):
    def setUp(self):
        with NamedTemporaryFile(
            mode="w", delete=False, delete_on_close=False
        ) as yaml_file:
            yaml_file.write(
                yaml.dump(
                    {
                        "1": {
                            "name": "pipo",
                            "index": 10,
                            "gid": [12, 13],
                            "info": {"description": "Example user"},
                        }
                    }
                )
            )
            self.yaml_database = yaml_file.name

    def test_search_with_base_init(self):
        yaml_engine = YamlEngine(self.yaml_database)

        _id, item = yaml_engine.search("1")
        assert_that(_id, equal_to("1"))
        assert_that(
            item,
            all_of(
                has_length(4),
                has_entries(
                    {
                        "name": "pipo",
                        "index": 10,
                        "gid": contains_exactly(12, 13),
                        "info": all_of(
                            has_length(1), has_entries({"description": "Example user"})
                        ),
                    }
                ),
            ),
        )

    def test_search_with_attributes_and_empty_init(self):
        yaml_engine = YamlEngine(
            self.yaml_database,
            database_item=YamlItem(
                item_mapper=MapByKey(empty_init=True),
                model={
                    "name": YamlAttribute(),
                    "group": YamlAttribute(["gid", 1]),
                    "info": YamlAttribute(["info", "description"]),
                },
            ),
        )

        _id, item = yaml_engine.search("1")
        assert_that(_id, equal_to("1"))
        assert_that(
            item,
            all_of(
                has_length(3),
                has_entries({"name": "pipo", "group": 13, "info": "Example user"}),
            ),
        )

    def test_search_with_attributes_and_base_init(self):
        yaml_engine = YamlEngine(
            self.yaml_database,
            database_item=YamlItem(
                model={
                    "name": YamlAttribute(),
                    "info": YamlAttribute(["info", "description"]),
                }
            ),
        )

        _id, item = yaml_engine.search("1")
        assert_that(_id, equal_to("1"))
        assert_that(
            item,
            all_of(
                has_length(4),
                has_entries(
                    {
                        "name": "pipo",
                        "index": 10,
                        "gid": contains_exactly(12, 13),
                        "info": "Example user",
                    }
                ),
            ),
        )

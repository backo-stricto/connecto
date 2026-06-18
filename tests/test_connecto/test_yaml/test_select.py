"""
Module to test the select operation of the YAML connector.
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


class TestYamlSelect(unittest.TestCase):
    def setUp(self):
        with NamedTemporaryFile(
            mode="w", delete=False, delete_on_close=False
        ) as yaml_file:
            yaml_file.write(
                yaml.dump(
                    {
                        i: {
                            "name": f"pipo {i}",
                            "index": i,
                            "gid": [i, i + 1],
                            "info": {"description": f"Example user {i}"},
                        }
                        for i in range(10)
                    }
                )
            )
            self.yaml_database = yaml_file.name

    def test_select_with_base_init(self):
        yaml_engine = YamlEngine(self.yaml_database)

        items = yaml_engine.select()

        assert_that(items, has_length(10))
        for _id, item in items:
            assert_that(
                item,
                all_of(
                    has_length(4),
                    has_entries(
                        {
                            "name": f"pipo {_id}",
                            "index": _id,
                            "gid": contains_exactly(_id, _id + 1),
                            "info": all_of(
                                has_length(1),
                                has_entries({"description": f"Example user {_id}"}),
                            ),
                        }
                    ),
                ),
            )

    def test_select_with_attributes_and_empty_init(self):
        yaml_engine = YamlEngine(
            self.yaml_database,
            database_item=YamlItem(
                item_mapper=MapByKey(empty_init=True),
                model={
                    "name": YamlAttribute(),
                    "info": YamlAttribute(["info", "description"]),
                },
            ),
        )

        items = yaml_engine.select()

        assert_that(items, has_length(10))
        for _id, item in items:
            assert_that(
                item,
                all_of(
                    has_length(2),
                    has_entries(
                        {
                            "name": f"pipo {_id}",
                            "info": f"Example user {_id}",
                        }
                    ),
                ),
            )

    def test_select_with_attributes_and_base_init(self):
        yaml_engine = YamlEngine(
            self.yaml_database,
            database_item=YamlItem(
                model={
                    "name": YamlAttribute(),
                    "info": YamlAttribute(["info", "description"]),
                }
            ),
        )

        items = yaml_engine.select()

        assert_that(items, has_length(10))
        for _id, item in items:
            assert_that(
                item,
                all_of(
                    has_length(4),
                    has_entries(
                        {
                            "name": f"pipo {_id}",
                            "index": _id,
                            "gid": contains_exactly(_id, _id + 1),
                            "info": f"Example user {_id}",
                        }
                    ),
                ),
            )

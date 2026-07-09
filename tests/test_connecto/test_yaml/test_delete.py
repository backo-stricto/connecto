"""
Module to test the delete operation of the YAML connector.
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
    empty,
)

from tempfile import NamedTemporaryFile
from connecto.yaml import YamlEngine, YamlItem, MapByKey, YamlAttribute

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest.core.helpers.hasmethod import hasmethod


class TestYamlDelete(unittest.TestCase):
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

    def test_delete_with_base_init(self):
        yaml_engine = YamlEngine(self.yaml_database)

        yaml_engine.delete("1")

        with open(self.yaml_database, "r") as yaml_file:
            assert_that(yaml.load(yaml_file.read(), Loader=yaml.Loader), empty())

    def test_delete_with_attributes_and_empty_init(self):
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

        yaml_engine.delete("1")

        with open(self.yaml_database, "r") as yaml_file:
            assert_that(yaml.load(yaml_file.read(), Loader=yaml.Loader), empty())

    def test_delete_with_attributes_and_base_init(self):
        yaml_engine = YamlEngine(
            self.yaml_database,
            database_item=YamlItem(
                model={
                    "name": YamlAttribute(),
                    "info": YamlAttribute(["info", "description"]),
                }
            ),
        )

        yaml_engine.delete("1")

        with open(self.yaml_database, "r") as yaml_file:
            assert_that(yaml.load(yaml_file.read(), Loader=yaml.Loader), empty())

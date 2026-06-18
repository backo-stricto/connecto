"""
Module to test the update operation of the YAML connector.
"""

import unittest
import yaml

from hamcrest import (
    assert_that,
    equal_to,
    contains_exactly,
    all_of,
    has_length,
    has_entries,
)

from tempfile import NamedTemporaryFile
from connecto.yaml import YamlEngine, YamlItem, MapByKey, YamlAttribute


class TestYamlUpdate(unittest.TestCase):
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

    def test_update_with_base_init(self):
        yaml_engine = YamlEngine(self.yaml_database)

        yaml_engine.save(
            "1",
            {
                "name": "molo",
                "gid": [10, 11],
                "info": {"description": "Updated user"},
            },
        )

        with open(self.yaml_database, "r") as yaml_file:
            database = yaml.load(yaml_file.read(), Loader=yaml.Loader)
            assert_that(
                database["1"],
                all_of(
                    has_length(3),
                    has_entries(
                        # Init base init mode, the item is completly replaced so
                        # the index key from the original file has been
                        # overriden
                        {
                            "name": "molo",
                            "gid": contains_exactly(10, 11),
                            "info": all_of(
                                has_length(1),
                                has_entries({"description": f"Updated user"}),
                            ),
                        }
                    ),
                ),
            )

    def test_create_with_attributes_and_empty_init(self):
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

        yaml_engine.save("1", {"name": "molo", "info": f"Updated user"})

        with open(self.yaml_database, "r") as yaml_file:
            database = yaml.load(yaml_file.read(), Loader=yaml.Loader)
            assert_that(
                database["1"],
                all_of(
                    has_length(2),
                    has_entries(
                        {
                            "name": f"molo",
                            "info": all_of(
                                has_length(1),
                                has_entries({"description": "Updated user"}),
                            ),
                        }
                    ),
                ),
            )

    def test_update_with_attributes_and_base_init(self):
        yaml_engine = YamlEngine(
            self.yaml_database,
            database_item=YamlItem(
                model={
                    "name": YamlAttribute(),
                    "info": YamlAttribute(["info", "description"]),
                }
            ),
        )

        yaml_engine.save("1", {"name": f"molo", "gid": 10, "info": "Updated user"})

        with open(self.yaml_database, "r") as yaml_file:
            database = yaml.load(yaml_file.read(), Loader=yaml.Loader)

            assert_that(
                database["1"],
                all_of(
                    has_length(3),
                    has_entries(
                        {
                            "name": f"molo",
                            "gid": 10,
                            "info": all_of(
                                has_length(1),
                                has_entries({"description": f"Updated user"}),
                            ),
                        }
                    ),
                ),
            )

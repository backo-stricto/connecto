"""
Module to test the create operation of the YAML connector.
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


class TestYamlCreate(unittest.TestCase):
    def setUp(self):
        with NamedTemporaryFile(
            mode="w", delete=False, delete_on_close=False
        ) as yaml_file:
            self.yaml_database = yaml_file.name

    def test_create_with_base_init(self):
        yaml_engine = YamlEngine(self.yaml_database)

        created_ids = []
        for i in range(10):
            _id = yaml_engine.create(
                {
                    "name": f"pipo {i}",
                    "gid": [i, i + 1],
                    "info": {"description": f"Example user {i}"},
                }
            )
            created_ids.append(_id)

        assert_that(len(set(created_ids)), equal_to(10))

        with open(self.yaml_database, "r") as yaml_file:
            database = yaml.load(yaml_file.read(), Loader=yaml.Loader)
            for i, _id in enumerate(created_ids):
                assert_that(
                    database[_id],
                    all_of(
                        has_length(3),
                        has_entries(
                            {
                                "name": f"pipo {i}",
                                "gid": contains_exactly(i, i + 1),
                                "info": all_of(
                                    has_length(1),
                                    has_entries({"description": f"Example user {i}"}),
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

        created_ids = []
        for i in range(10):
            _id = yaml_engine.create({"name": f"pipo {i}", "info": f"Example user {i}"})
            created_ids.append(_id)

        assert_that(len(set(created_ids)), equal_to(10))

        with open(self.yaml_database, "r") as yaml_file:
            database = yaml.load(yaml_file.read(), Loader=yaml.Loader)
            for i, _id in enumerate(created_ids):
                assert_that(
                    database[_id],
                    all_of(
                        has_length(2),
                        has_entries(
                            {
                                "name": f"pipo {i}",
                                "info": all_of(
                                    has_length(1),
                                    has_entries({"description": f"Example user {i}"}),
                                ),
                            }
                        ),
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

        created_ids = []
        for i in range(10):
            _id = yaml_engine.create(
                {"name": f"pipo {i}", "gid": i, "info": f"Example user {i}"}
            )
            created_ids.append(_id)

        assert_that(len(set(created_ids)), equal_to(10))

        with open(self.yaml_database, "r") as yaml_file:
            database = yaml.load(yaml_file.read(), Loader=yaml.Loader)
            for i, _id in enumerate(created_ids):
                assert_that(
                    database[_id],
                    all_of(
                        has_length(3),
                        has_entries(
                            {
                                "name": f"pipo {i}",
                                "gid": i,
                                "info": all_of(
                                    has_length(1),
                                    has_entries({"description": f"Example user {i}"}),
                                ),
                            }
                        ),
                    ),
                )

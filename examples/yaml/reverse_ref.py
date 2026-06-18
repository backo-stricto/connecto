from connecto.yaml import YamlEngine, YamlItem, YamlAttribute, MapByKey
from connecto.reverse_ref import ReverseRef
from stricto.filter import SFilter, Operator
from stricto import Dict, List, String

if __name__ == "__main__":
    group_database_item = YamlItem()
    yaml_group_engine = YamlEngine("group.yaml", database_item=group_database_item)

    yaml_user_engine = YamlEngine(
        "user.yaml",
        database_item=YamlItem(
            model={
                "name": YamlAttribute(),
                "group": ReverseRef(
                    select_engine=YamlEngine(
                        "group.yaml", database_item=YamlItem(model={})
                    ),
                    # Specifies the filter as a nested list of SFilter
                    # parameters
                    # Needs support for constants
                    item_filter=YamlItem(
                        item_mapper=MapByKey(empty_init=True),
                        model=(
                            "$.users",
                            Operator.CONTAINS,
                            ("@", Operator.EQ, YamlAttribute(["name"])),
                        ),
                    ),
                ),
            }
        ),
    )

    user_id = yaml_user_engine.create(
        {"name": "pipo", "gid": 12, "description": "Example user"}
    )
    group_id = yaml_group_engine.create({"name": "test_group", "users": ["pipo"]})

    print(f"Item {user_id} created.")
    print(yaml_user_engine.search(user_id))
    print()

    yaml_group_engine.delete(group_id)

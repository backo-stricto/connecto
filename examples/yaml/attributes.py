from connecto.yaml import YamlEngine, YamlItem, YamlAttribute

if __name__ == "__main__":
    yaml_engine = YamlEngine(
        "test.yaml", database_item=YamlItem(model={"login": YamlAttribute(["name"])})
    )
    item_id = yaml_engine.create(
        {"login": "pipo", "gid": 12, "description": "Example user"}
    )
    print(f"Item {item_id} created.")
    print(yaml_engine.search(item_id))
    print()

    yaml_engine.save(
        item_id, {"login": "molo", "gid": 13, "description": "Updated user"}
    )
    print(f"Item {item_id} updated.")
    print(yaml_engine.search(item_id))
    print()

    yaml_engine.create({"login": "bato", "gid": 10, "description": "New user"})
    print(f"Selected items:")
    print(yaml_engine.select())
    print()

    yaml_engine.delete(item_id)
    print(f"Item {item_id} deleted.")

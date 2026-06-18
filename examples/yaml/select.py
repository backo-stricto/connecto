import json

from connecto.yaml import YamlEngine, YamlItem, YamlAttribute

if __name__ == "__main__":
    yaml_engine = YamlEngine("test.yaml", database_item=YamlItem())
    yaml_engine.create({"login": "pipo", "gid": 12, "description": "Example user"})
    yaml_engine.create({"login": "molo", "gid": 13, "description": "Other user"})
    print("Selected items:")
    print(json.dumps(yaml_engine.select(), indent=2))

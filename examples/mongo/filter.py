from connecto.item_filter import ItemFilterCompiler, AttributeFilterCompiler, FilterCompiler
from stricto.filter import SFilter, Operator

import json

def mongo_and(conditions):
    return {
            "compound": {
                "must": conditions
                }
            }

def mongo_or(conditions):
    return {
            "compound": {
                "should": conditions
                }
            }

def mongo_eq(mongo_path, value):
    return {
            "equals": {
                "path": mongo_path,
                "value": value
            }
            }

def mongo_lt(mongo_path, value):
    return {
            "range": {
                "path": mongo_path,
                "lt": value
                }
            }

def mongo_lte(mongo_path, value):
    return {
            "range": {
                "path": mongo_path,
                "lte": value
                }
            }

def mongo_gt(mongo_path, value):
    return {
            "range": {
                "path": mongo_path,
                "gt": value
                }
            }


def mongo_gte(mongo_path, value):
    return {
            "range": {
                "path": mongo_path,
                "gte": value
                }
            }

def mongo_reg(mongo_path, value):
    return {
            "regex": {
                "path": mongo_path,
                "query": value
                }
            }

class MongoFilter(ItemFilterCompiler):
    def select_and(self, conditions):
        return mongo_and(conditions)
    def select_or(self, conditions):
        return mongo_or(conditions)

    def select_eq(self, attribute_path, value):
        return mongo_eq('.'.join(attribute_path), value)

    def select_lt(self, attribute_path, value):
        return mongo_lt('.'.join(attribute_path), value)

    def select_lte(self, attribute_path, value):
        return mongo_lte('.'.join(attribute_path), value)

    def select_gt(self, attribute_path, value):
        return mongo_gt('.'.join(attribute_path), value)

    def select_gte(self, attribute_path, value):
        return mongo_gte('.'.join(attribute_path), value)

    def select_reg(self, attribute_path, value):
        return mongo_reg('.'.join(attribute_path), value)

class MongoField(AttributeFilterCompiler):
    def __init__(self, mongo_path):
        self.mongo_path = mongo_path

    def select_eq(self, value):
        return mongo_eq(self.mongo_path, value)

    def select_gt(self, value):
        return mongo_gt(self.mongo_path, value)

    def select_gte(self, value):
        return mongo_gte(self.mongo_path, value)

    def select_lt(self, value):
        return mongo_lt(self.mongo_path, value)

    def select_lte(self, value):
        return mongo_lte(self.mongo_path, value)

    def select_reg(self, value):
        return mongo_reg(self.mongo_path, value)

if __name__ == "__main__":
    filter_compiler = FilterCompiler(
            {
                "login": MongoField("user.name"),
                "count": MongoField("number")
            },
            MongoFilter()
            )
    sfilter = SFilter("$",  Operator.AND, [
            SFilter("group.uid", Operator.EQ, "users"),
            SFilter("$", Operator.OR, [
                SFilter("login", Operator.EQ, "admin"),
                SFilter("count", Operator.GT, 500)
                ])
            ])
    print(f"SFilter: {sfilter}")
    print(f"Mongo search query:\n{json.dumps(filter_compiler.compile_filter(sfilter), indent=2)}")

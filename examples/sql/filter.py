from connecto.item_filter import ItemFilterCompiler, AttributeFilterCompiler, FilterCompiler
from stricto.filter import SFilter, Operator

def sql_and(conditions):
    return f"({' AND '.join(conditions)})"

def sql_or(conditions):
    return f"({' OR '.join(conditions)})"

def sql_eq(column, value):
    return f"({column} = {value})"

def sql_lt(column, value):
    return f"({column} < {value})"

def sql_lte(column, value):
    return f"({column} <= {value})"

def sql_gt(column, value):
    return f"({column} > {value})"

def sql_gte(column, value):
    return f"({column} >= {value})"

class SqlFilter(ItemFilterCompiler):
    def select_and(self, conditions):
        return sql_and(conditions)
    def select_or(self, conditions):
        return sql_or(conditions)

    def select_eq(self, attribute_path, value):
        return sql_eq(attribute_path[0], value)

    def select_lt(self, attribute_path, value):
        return sql_lt(attribute_path[0], value)

    def select_lte(self, attribute_path, value):
        return sql_lt(attribute_path[0], value)

    def select_gt(self, attribute_path, value):
        return sql_lt(attribute_path[0], value)

    def select_gte(self, attribute_path, value):
        return sql_lt(attribute_path[0], value)

class SqlColumn(AttributeFilterCompiler):
    def __init__(self, sql_column):
        self.sql_column = sql_column

    def select_eq(self, value):
        return sql_eq(self.sql_column, value)

    def select_gt(self, value):
        return sql_gt(self.sql_column, value)

    def select_gte(self, value):
        return sql_gte(self.sql_column, value)

    def select_lt(self, value):
        return sql_lt(self.sql_column, value)

    def select_lte(self, value):
        return sql_lte(self.sql_column, value)

    def select_reg(self, value):
        raise NotImplementedError("SQL does not support REG filters.")


if __name__ == "__main__":
    filter_compiler = FilterCompiler(
            {
                "login": SqlColumn("name"),
                "count": SqlColumn("number")
            },
            SqlFilter()
            )
    sfilter = SFilter("$",  Operator.AND, [
            SFilter("group", Operator.EQ, "users"),
            SFilter("$", Operator.OR, [
                SFilter("login", Operator.EQ, "admin"),
                SFilter("count", Operator.GT, 500)
                ])
            ])
    print(f"SFilter: {sfilter}")
    print(f"SQL WHERE: {filter_compiler.compile_filter(sfilter)}")

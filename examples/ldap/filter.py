
from connecto.item_filter import ItemFilterCompiler, AttributeFilterCompiler, FilterCompiler
from stricto.filter import SFilter, Operator

def ldap_and(conditions):
    return f"(&{''.join(conditions)})"

def ldap_or(conditions):
    return f"(&{''.join(conditions)})"

def ldap_eq(attribute, value):
    return f"({attribute}={value})"

def ldap_not(condition):
    return f"(!{condition})"

def ldap_lt(attribute, value):
    return ldap_and([
        ldap_lte(attribute, value),
        ldap_not(
            ldap_eq(attribute, value)
            )
        ])

def ldap_lte(attribute, value):
    return f"({attribute}<={value})"

def ldap_gt(attribute, value):
    return ldap_and([
        ldap_gte(attribute, value),
        ldap_not(
            ldap_eq(attribute, value)
            )
        ])


def ldap_gte(attribute, value):
    return f"({attribute}<={value})"

class LdapFilter(ItemFilterCompiler):
    def select_and(self, conditions):
        return ldap_and(conditions)
    def select_or(self, conditions):
        return ldap_or(conditions)

    def select_eq(self, attribute_path, value):
        return ldap_eq(attribute_path[0], value)

    def select_lt(self, attribute_path, value):
        return ldap_lt(attribute_path[0], value)

    def select_lte(self, attribute_path, value):
        return ldap_lt(attribute_path[0], value)

    def select_gt(self, attribute_path, value):
        return ldap_lt(attribute_path[0], value)

    def select_gte(self, attribute_path, value):
        return ldap_lt(attribute_path[0], value)

class LdapAttribute(AttributeFilterCompiler):
    def __init__(self, ldap_attribute):
        self.ldap_attribute = ldap_attribute

    def select_eq(self, value):
        return ldap_eq(self.ldap_attribute, value)

    def select_gt(self, value):
        return ldap_gt(self.ldap_attribute, value)

    def select_gte(self, value):
        return ldap_gte(self.ldap_attribute, value)

    def select_lt(self, value):
        return ldap_lt(self.ldap_attribute, value)

    def select_lte(self, value):
        return ldap_lte(self.ldap_attribute, value)

    def select_reg(self, value):
        raise NotImplementedError("LDAP does not support REG filters.")


if __name__ == "__main__":
    filter_compiler = FilterCompiler(
            {
                "name": LdapAttribute("cn"),
                "uid": LdapAttribute("uidNumber")
            },
            LdapFilter()
            )
    sfilter = SFilter("$",  Operator.AND, [
            SFilter("objectClass", Operator.EQ, "posixAccount"),
            SFilter("$", Operator.OR, [
                SFilter("name", Operator.EQ, "admin"),
                SFilter("uid", Operator.GT, 500)
                ])
            ])
    print(f"SFilter: {sfilter}")
    print(f"LDAP filter: {filter_compiler.compile_filter(sfilter)}")

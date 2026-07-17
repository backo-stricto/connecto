"""Features required to implement database filters."""

from stricto.filter import Operator

from jsonpath import JSONPath

from .utils import nested_data_path


class ItemFilterCompiler:
    """Generic filter compiler that defines operations at the model level, for
    attributes **not** included in the model.

    AND and OR operations are also implemented at the ItemFilter level because
    they are compound operations that do not depend on each attribute.

    The `attribute_path` passed to each other operation is the compiled absolute
    path of the item the SFilter is currently attempting to match, specified as
    a list of int/str.

    See FilterCompiler.compile_filter() for how and when each operation of the
    ItemFilterCompiler is called.

    The implementation is free to chose how to handle the path to an attribute
    not included in the model. For example, the last component of the path can
    be considered as an SQL column name, raising an error if the length of the
    path is greater than 1. The path could also be interpreted as a JSONPath
    within a YAML, or as a Mongo path to a field.

    The format of compiled operations is completely free. It can be anything
    that can be interpreted by the DatabaseConnection to perform a selection.

    Each implementation is free to support only a subset of the available
    operations. By default, a NotImplementedError is raised when attempting to
    compile an operation that is not available.
    """

    def select_and(self, conditions):
        """Compounds a logical AND from compiled conditions."""
        raise NotImplementedError("The ItemMapper does not support AND filters.")

    def select_or(self, conditions):
        """Compounds a logical OR from compiled conditions."""
        raise NotImplementedError("The ItemMapper does not support OR filters.")

    def select_eq(self, attribute_path, value):
        """Compiles a statement that matches when the field at attribute_path is
        equal to value.
        """
        raise NotImplementedError("The ItemMapper does not support EQ filters.")

    def select_gt(self, attribute_path, value):
        """Compiles a statement that matches when the field at attribute_path is
        greater than value.
        """
        raise NotImplementedError("The ItemMapper does not support GT filters.")

    def select_gte(self, attribute_path, value):
        """Compiles a statement that matches when the field at attribute_path is
        greater than or equal to value.
        """
        raise NotImplementedError("The ItemMapper does not support GTE filters.")

    def select_lt(self, attribute_path, value):
        """Compiles a statement that matches when the field at attribute_path is
        less than value.
        """
        raise NotImplementedError("The ItemMapper does not support LT filters.")

    def select_lte(self, attribute_path, value):
        """Compiles a statement that matches when the field at attribute_path is
        less than or equal to value.
        """
        raise NotImplementedError("The ItemMapper does not support LTE filters.")

    def select_reg(self, attribute_path, regex):
        """Compiles a statement that matches when the field at attribute_path
        matches the regex.
        """
        raise NotImplementedError("The ItemMapper does not support REG filters.")


class AttributeFilterCompiler:
    """A set of operations to implement by a DatabaseAttribute to support
    database filtering.

    If a DatabaseAttribute does not implement this interface, the default
    ItemFilter will be used instead.

    Each implementation is free to support only a subset of the available
    operations. By default, a NotImplementedError is raised when attempting to
    compile an operation that is not available.
    """

    def select_eq(self, value):
        """Compiles a statement that matches when the attribute is equal to
        value.
        """
        raise NotImplementedError("The Attribute does not support EQ filters.")

    def select_gt(self, value):
        """Compiles a statement that matches when the attribute is greater than
        value.
        """
        raise NotImplementedError("The Attribute does not support GT filters.")

    def select_gte(self, value):
        """Compiles a statement that matches when the attribute is greater than
        or equal to value.
        """
        raise NotImplementedError("The Attribute does not support GTE filters.")

    def select_lt(self, value):
        """Compiles a statement that matches when the attribute is less than
        value.
        """
        raise NotImplementedError("The Attribute does not support LT filters.")

    def select_lte(self, value):
        """Compiles a statement that matches when the attribute is less than or
        equal to value.
        """
        raise NotImplementedError("The Attribute does not support LTE filters.")

    def select_reg(self, regex):
        """Compiles a statement that matches when the attribute matches regex."""
        raise NotImplementedError("The Attribute does not support REG filters.")


class FilterCompiler:
    """An object that can be used to compile database filters from the specified
    model and the item_filter.

    :param model: A DatabaseItem model with attributes that might implement
    AttributeFilterCompiler
    :param item_filter: An ItemFilterCompiler used to compile filters for fields that do
    not correspond to an attribute implementing AttributeFilter in the model.
    Also provides implemenation of AND and OR operations.
    """

    def __init__(self, model, item_filter):
        self.model = model
        self.item_filter = item_filter

        self._default_select_compilers = {
            Operator.AND: item_filter.select_and,
            Operator.OR: item_filter.select_or,
            Operator.EQ: item_filter.select_eq,
            Operator.REG: item_filter.select_reg,
            Operator.GT: item_filter.select_gt,
            Operator.GTE: item_filter.select_gte,
            Operator.LT: item_filter.select_lt,
            Operator.LTE: item_filter.select_lte,
        }
        self._attribute_select_compilers = {
            Operator.EQ: lambda attribute_filter: attribute_filter.select_eq,
            Operator.REG: lambda attribute_filter: attribute_filter.select_reg,
            Operator.GT: lambda attribute_filter: attribute_filter.select_gt,
            Operator.GTE: lambda attribute_filter: attribute_filter.select_gte,
            Operator.LT: lambda attribute_filter: attribute_filter.select_lt,
            Operator.LTE: lambda attribute_filter: attribute_filter.select_lte,
        }

    def _build_default_filter(self, model, model_path, sfilter):
        # Allows access to sfilter private attributes
        # pylint: disable=W0212
        if sfilter._operator in [Operator.AND, Operator.OR]:
            compiled_conditions = []
            for s_filter in sfilter._value:
                compiled_conditions.append(
                    self._build_filter(model, model_path, s_filter)
                )
            return self._default_select_compilers[sfilter._operator](
                compiled_conditions
            )
        return self._default_select_compilers[sfilter._operator](
            model_path, sfilter._value
        )
        # pylint: enable=W0212

    def _build_attribute_filter(self, attribute, sfilter):
        # Allows access to sfilter private attributes
        # pylint: disable=W0212
        if sfilter._operator in [Operator.AND, Operator.OR]:
            compiled_conditions = []
            for s_filter in sfilter._value:
                compiled_conditions.append(
                    self._build_attribute_filter(attribute, s_filter)
                )
            return self._default_select_compilers[sfilter._operator](
                compiled_conditions
            )
        return self._attribute_select_compilers[sfilter._operator](attribute)(
            sfilter._value
        )
        # pylint: enable=W0212

    def _build_filter(self, model, model_path, sfilter):
        # Allows access to sfilter private attributes
        # pylint: disable=W0212
        if isinstance(model, (list, dict)):
            attribute = JSONPath(sfilter._path).parse(model)
        elif isinstance(model, tuple):
            attribute = JSONPath(sfilter._path).parse(list(model))
        else:
            # Single attribute model
            return self._build_attribute_filter(model, sfilter)

        # attribute is the result of the jsonpath selection, i.e. a list
        if len(attribute) == 1:
            if isinstance(attribute[0], AttributeFilterCompiler):
                return self._build_attribute_filter(attribute[0], sfilter)
            return self._build_default_filter(
                attribute[0],
                model_path + nested_data_path.from_jsonpath(sfilter._path),
                sfilter,
            )
        return self._build_default_filter(
            {}, model_path + nested_data_path.from_jsonpath(sfilter._path), sfilter
        )
        # pylint: enable=W0212

    def compile_filter(self, item_sfilter):
        """Compiles the specified SFilter into a database filter.

        The SFilter is parsed and interpreted along the model as follows:
        1. the current path of the SFilter is computed according to its parents.
        For example, the path of the EQ operator in `SFilter("$.root", AND,
        [..., ("data", OR, [..., EQ, "foo"])` is `["root", "data"]`.
        2. if an attribute implementing AttributeFilterCompiler is found at that
        path in the model, `attribute.select_<op>(value)` is called, where value
        is the value to match in the current SFilter.
        3. else, the filter is compiled with the generic
        `item_filter.select_<op>(path, value)`

        :param item_sfilter: An SFilter to compile into a database filter
        """
        return self._build_filter(self.model, [], item_sfilter)

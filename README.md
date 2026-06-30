# Connecto

The purpose of connecto is to interface database schemes of any type with an
user defined JSON based interface.

It is designed with two main objectives in mind:
1. Provide a set of ready to use connectors that allow end users to easily build
   an interface to manage item in a database.
2. A set of interfaces and methods that can be used by developers to easily
   build connectors to new databases that are not already supported by
   `connecto`.

# Examples

Usage examples are available in the `examples` folder.

For examples of connector implementations, see the corresponding `connecto`
submodule (e.g. `connecto.yaml`, `connecto.ldap`, `connecto.sql`...).

Also check the [wiki](https://github.com/backo-stricto/connecto/wiki) for
details on working principles of `connecto`. The wiki also includes tutorials to
learn how to implement a full featured connector for a new database.

# Developement

## Tests

Run the test suite:
```bash
uv run -m unittest tests
```

## Formatting

Use `black` to format files before staging changes:
```bash
uv run --dev -m black $(git ls-files '*.py')
```

## Linting

Use `pylint` to format files before staging changes:
```bash
uv run --dev -m pylint $(git ls-files '*.py')
```


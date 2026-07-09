# Connecto

`connecto` provides a low-code API that allow you to build JSON based interfaces
to any type of database.

It allows you to precisely describe a specification of the expected JSON-like
structure and where to retrieve each field from the dabatase. `connecto` will
then efficiently handle the logic required to search, select, delete and update
items in the database, so you only need to focus on the necessary code that is
required to run the application.

`connecto` is designed with two main objectives in mind:
1. Provide a set of ready to use connectors that allow end users to easily build
   an interface to manage item in a database.
2. A set of interfaces and methods that can be used by developers to easily
   build connectors to new databases that are not already supported by
   `connecto`.

# Examples

Usage examples are available in the `examples` folder. See the
[wiki](https://github.com/backo-stricto/connecto/wiki/Introduction) for more
examples with detailed explanations.

For examples of connector implementations, see the corresponding `connecto`
submodule (e.g. `connecto.yaml`, `connecto.ldap`, `connecto.sql`...).

Also check the [wiki](https://github.com/backo-stricto/connecto/wiki) for
details on [working
principles](https://github.com/backo-stricto/connecto/wiki/WorkingPrinciples) of
`connecto`. The wiki also includes
[tutorials](https://github.com/backo-stricto/connecto/wiki/BasicConnectorTutorial)
to learn how to implement a full featured connector for a new database.

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


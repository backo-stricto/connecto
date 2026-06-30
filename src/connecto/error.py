"""Defines database related exceptions."""


class ItemNotFound(Exception):
    """Exception raised if an item could not be found when executing a search
    request against a database.
    """

    def __init__(self, _id, database):
        super().__init__(f"Item {_id} could not be found in database {database}")

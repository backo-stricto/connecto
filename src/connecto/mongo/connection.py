"""Provides the implementation of a DatabaseConnection to a YAML file."""

from typing import Any

from pymongo import MongoClient
from pymongo.uri_parser import parse_uri
from bson.objectid import ObjectId

from ..connection import DatabaseConnection
from .request import (
    MongoSearchRequest,
    MongoSearchResponse,
    MongoCreateRequest,
    MongoCreateResponse,
    MongoDeleteRequest,
    MongoDeleteResponse,
    MongoUpdateRequest,
    MongoUpdateResponse,
    MongoSelectRequest,
    MongoSelectResponse,
)
from ..error import DBError, ItemNotFound


class MongoConnection(DatabaseConnection):
    """Database connection used to perform operations on a YAML file.

    The `yaml_path` parameter allows to specify where is the root of the
    collection of items within the YAML file, if it's not the root of the file
    itself. See utils.nested_data_path for how to specify the path as a list of
    str / int.

    For example, if `database.yaml` looks like
    ```yaml
    config:
      some: "value"
      data: 1
    users:
      collection:
        1: <user 1>
        2: <user 2>
        ...
    ```
    the connection should be initialized as
    ```python
    MongoConnection("database.yaml", ["users", "collection"])
    ```


    :param file_path: Path to the YAML database
    :param yaml_path: A nested data path to the root of the collection within
    the file.
    """

    def __init__(self, connection_string:str, collection_name:str, **kwargs):
        """


        :param connection_string: the uri to pass to MongoClient
        :type connection_string: str
        :param collection_name: the name of the collection
        :type collection_name: str
        """
        self._connection_string = connection_string
        self._collection_name = collection_name

        self._db = MongoClient(self._connection_string, **kwargs)

        self._database = self._db.get_default_database()
        self._collection = self._database[self._collection_name]
        DatabaseConnection.__init__(self)

    def connect(self)-> Any:
        """Try to make a connection to the mongodb

        :raise BDError: Raise an error in case of database Error

        """
        try:
            return self._db.server_info()
        except Exception as e:
            raise DBError(
                'Mongo connection error at "{0}"', self._connection_string
            ) from e

    def close(self)-> Any:
        """Close the mongodb connection

        :raise DBError: Raise an error in case of database Error

        """
        try:
            return self._db.close()
        except Exception as e:
            raise DBError('Mongo close error at "{0}"', self._connection_string) from e

    def execute_search(self, request: MongoSearchRequest)-> MongoSearchResponse:

        try:
            db_filter = {"_id": ObjectId(request._id)}
            o = self._collection.find_one(db_filter)
        except Exception as e:
            raise DBError(
                'Mongo connection error while "{0}.find_one()"', self._collection_name
            ) from e

        if o is None:
            raise ItemNotFound(
                '_id "{0}" not found in collection "{1}"', request._id, self._collection_name
            )
        o["_id"] = request._id

        return MongoSearchResponse(o)

    def execute_create(self, request: MongoCreateRequest)-> MongoCreateResponse:
        try:
            result = self._collection.insert_one(request.obj)
        except Exception as e:
            raise DBError(
                'Mongo connection error while "{0}.insert_one()"', self._collection_name
            ) from e

        return MongoCreateResponse(result.inserted_id)

    def execute_delete(self, request: MongoDeleteRequest)-> MongoDeleteResponse:

        try:
            db_filter = {"_id": ObjectId(request._id)}
            result = self._collection.delete_one(db_filter)
        except Exception as e:
            raise DBError(
                'Mongo connection error while "{0}.delete_one()"', self._collection_name
            ) from e

        if result.deleted_count != 1:
            raise DBError(
                'Mongo connection error while "{0}.delete_one()"', self._collection_name
            ) from e
        return MongoDeleteResponse()

    def execute_update(self, request: MongoUpdateRequest) -> MongoUpdateResponse:

        o = request.obj
        o["_id"] = ObjectId(request._id)
        try:
            result = self._collection.find_one_and_replace(
                {"_id": ObjectId(request._id)}, o, {"upsert": True}
            )
        except Exception as e:
            raise DBError(
                'Mongo connection error while "{0}.find_one_and_replace()"',
                self._collection_name,
            ) from e


        return MongoUpdateResponse()

    def execute_select(self, request: MongoSelectRequest) -> MongoSelectResponse:


        result_list = list(
            self._collection.find({}, {}
            #.sort(sort_object)
            #.skip(num_of_element_to_skip)
            #.limit(page_size)
        ))


        items = {}
        
        return MongoSelectResponse(items)

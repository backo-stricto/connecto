"""Module defining common set up for DatabaseEngine operations tests."""

import unittest

from unittest.mock import MagicMock

from connecto.connection import DatabaseConnection


def mock_execute_request(request):
    """Method that can be used as a side effect to mock the execution of a
    request, assuming the response of the request is already contained in its
    response attribute.
    """
    return request.response


class OperationTestCase(unittest.TestCase):
    """A TestCase that can be used by DatabaseEngine operation tests to set up
    a bunch of useful mocks.
    """

    def setUp(self):
        self.default_connection = MagicMock(DatabaseConnection)
        self.custom_connection = MagicMock(DatabaseConnection)

        self.mock_responses = [
            MagicMock(name=f"mock response {i}") for i in range(9)
        ]  # Database specific type
        self.mock_requests = [
            MagicMock(
                response=self.mock_responses[i], connection=self.default_connection
            )
            for i in range(9)
        ]

        for mock_request in self.mock_requests[:4]:
            mock_request.connection = self.default_connection
        for mock_request in self.mock_requests[4:]:
            mock_request.connection = self.custom_connection

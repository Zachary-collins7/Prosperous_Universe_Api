"""
This module defines the AuthMarker class which is used to check if a user is
authorized to access the API.
"""

from abc import ABC, abstractmethod


class AuthMarker(ABC):
    """
    AuthMarker class to authenticate user and get user data
    """

    @abstractmethod
    def check_auth(self) -> bool:
        """checks if AuthMarker is authorized"""

    @abstractmethod
    def get_user(self):
        """returns an instance of PUUser"""

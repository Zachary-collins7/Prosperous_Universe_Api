"""
This module defines the AuthProviderMarker class which is used to check if a
user is authorized to access the API.
"""

from abc import ABC, abstractmethod

from puapi.models.pu_user import PUUser


class AuthProviderMarker(ABC):
    """
    AuthProviderMarker class to authenticate user and get user data
    """

    @abstractmethod
    def authenticate(self) -> bool:
        """authenticate the user"""

    @abstractmethod
    def check_auth(self) -> bool:
        """checks if AuthProviderMarker is authorized"""

    @abstractmethod
    def get_user(self) -> PUUser:
        """
        returns an instance of PUUser with the user's data if the user
        is authenticated or raises an exception
        """

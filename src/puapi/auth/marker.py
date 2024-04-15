from abc import ABC, abstractmethod


class AuthMarker(ABC):

    @abstractmethod
    def check_auth(self) -> bool:
        """checks if AuthMarker is authorized"""

    @abstractmethod
    def get_user(self):
        """returns an instance of PUUser"""

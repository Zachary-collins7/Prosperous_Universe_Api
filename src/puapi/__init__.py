"""
Prosperous Universe API
"""

from puapi.options import Options


class ProsperousUniverseAPI:
    """
    Prosperous Universe API class to work with the Prosperous Universe API
    """

    def __init__(self, options: Options) -> None:
        self.__options = options
        self.__username = self.__options.apex_email
        self.__password = self.__options.apex_password
        self.__cookies = self.__options.cookies

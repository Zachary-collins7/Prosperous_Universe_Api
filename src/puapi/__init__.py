from puapi.options import Options


class ProsperousUniverseAPI:
    def __init__(self, options: Options) -> None:
        self.__options = options
        self.__username = self.__options.apex_email
        self.__password = self.__options.apex_password
        self.__cookies = self.__options.cookies

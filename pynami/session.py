from pynami.schemas.search import SearchSchema
from pynami.schemas.mgl import SearchMitgliedSchema
from pynami.net.connect import Connector


class Session:
    
    def __init__(self, config, **kwargs):
        self.__config = config | kwargs
        self.connector = Connector()
        self.current_user = None

    def search(self, **kwargs):
        if not kwargs:
            kwargs.update({})
        params = {'searchedValues': SearchSchema().dumps(kwargs, separators=(',', ':'))}
        response_content = self.connector.search(**params)
        return SearchMitgliedSchema().load(response_content, many=True)

    def __enter__(self, username=None, password=None):
        """
        Authenticate the user in the NaMi-API and save the logged in user for later usage.
        Args:
            @param username: The NaMi username, which is your member-id.
            password (:obj:`str`, optional): Your NAMI password
        """
        assert username or "username" in self.__config, "Provide a username either by config or argument"
        assert password or "password" in self.__config, "Provide a password either by config or argument"
        if not username or not password:
            username = self.__config['username']
            password = self.__config['password']
        self.connector.authenticate(username, password)
        self.current_user = next(iter(self.search(mitgliedsNummer=username)), None)
        if not self.current_user:
            raise ValueError(f"Login not possible for User {username}.")
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.connector.logout()
        if exception_type is None:
            return True

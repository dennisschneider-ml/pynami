from .data.exceptions import NamiHTTPException, NamiResponseSuccessException, NamiResponseTypeException
from .data.constants import URLS, DEFAULT_PARAMS
from .schemas.search import SearchSchema
from .schemas.mgl import SearchMitgliedSchema

import requests


class Session(object):
    
    def __init__(self, config, **kwargs):
        self.session = requests.Session()
        self.__config = config
        self.__config.update(kwargs)

    def search(self, **kwargs):
        """
        Run a search for members

        Todo:
            * Check search terms and formatting. Also some search keys can only
              be used mutually exclusive.

        Args:
            **kwargs: Search keys and words. Be advised that some search words
                must  have a certain formatting or can only take a limited
                amount of values.

        Returns:
            :obj:`list` of :class:`~.mgl.SearchMitglied`: The search
            results

        See also:
            :class:`~.search.SearchSchema` for a complete list of search
            keys
        """
        # this is just a default search
        if not kwargs:
            kwargs.update({})
        params = DEFAULT_PARAMS
        params['searchedValues'] = SearchSchema().dumps(kwargs, separators=(',', ':'))
        r = self.session.get(URLS['SEARCH'], params=params)
        return SearchMitgliedSchema().load(self._check_response(r), many=True)

    def auth(self, username=None, password=None):
        """
        Authenticate against the |NAMI| |API|. This stores the jsessionId
        cookie in the requests session. Therefore this needs to be called only
        once.

        This also stores your id (not the Mitgliednummer) for later purposes.

        Args:
            username (:obj:`str`, optional): The |NAMI| username. Which is your
                Mitgliedsnummer
            password (:obj:`str`, optional): Your NAMI password

        Returns:
            :class:`requests.Session`: The requests session, including the
            auth cookie
        """
        if not username or not password:
            username = self.__config['username']
            password = self.__config['password']

        payload = {
            'Login': 'API',
            'username': username,
            'password': password
        }

        url = URLS['AUTH']
        r = self.session.post(url, data=payload)
        if r.status_code != 200:
            raise ValueError('Authentication failed!')

        # Get the id of the user
        myself = self.search(mitgliedsNummer=username)
        if len(myself) == 1:
            self.__config['id'] = myself[0].id
            self.__config['stammesnummer'] = myself[0].gruppierungId
        else:
            raise ValueError(f'Received {len(myself)} search results while '
                             f'searching for myself!')
        return self.session

    def _check_response(self, response):
        """
        Check a requests response object if the |NAMI| response looks ok.
        This currently checks some very basic things.

        Raises:
            NamiHTTPException: When |HTTP| communication failes
            NamiResponseSuccessException: When the |NAMI| returns an error
        """
        if response.status_code != requests.codes.ok:
            raise NamiHTTPException(response.status_code)
        if response.headers['Content-Type'] == 'application/pdf':
            return response.content
        rjson = response.json()
        if not rjson['success']:
            raise NamiResponseSuccessException()

        # allowed response types are: OK, INFO, WARN, ERROR, EXCEPTION
        if rjson['responseType'] not in ['OK', 'INFO', None]:
            raise NamiResponseTypeException(rjson['responseType'])
        return rjson['data']

    def __enter__(self):
        self.auth()
        return self

    def logout(self):
        """This should be called at the end of the communication. It is called
        when exiting through the :meth:`~contextmnager.__exit__` method.
        """
        url = URLS['LOGOUT']
        r = self.session.get(url)
        if r.status_code != 204:
            self._check_response(r)

    def __exit__(self, exception_type, exception_value, traceback):
        try:
            self.logout()
        except NamiHTTPException as ex:
            print(f'NamiHTTPException during logout: {ex}')
        if exception_type is None:
            return True

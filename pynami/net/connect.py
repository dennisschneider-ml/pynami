import requests

from pynami import NamiHTTPException, NamiResponseSuccessException, NamiResponseTypeException
from pynami.data.constants import URLS, DEFAULT_PARAMS


class Connector:

    def __init__(self):
        self.session = requests.Session()

    def authenticate(self, username=None, password=None):
        payload = {
            "Login": "API",
            "username": username,
            "password": password
        }
        url = URLS["AUTH"]
        response = self.session.post(url, data=payload)
        if response.status_code != 200:
            raise ValueError("Authentication failed!")

    def logout(self):
        url = URLS["LOGOUT"]
        response = self.session.get(url)
        if response.status_code != 204:
            self._check_response(response)

    def search(self, **params):
        params = DEFAULT_PARAMS | params
        response = self.session.get(URLS["SEARCH"], params=params)
        return self._check_response(response)

    @staticmethod
    def _check_response(response):
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


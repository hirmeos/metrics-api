import os
from paste.fixture import TestApp
from api import app


class App(TestApp):
    _token = ''

    def __init__(self):
        middleware = []
        self.auth_headers = self.get_auth_headers(self._token)
        TestApp.__init__(self, app.wsgifunc(*middleware))

    def get_auth_headers(self, token):
        return {
            "Authorization": "Bearer {}".format(token),
            "Content-Type": "application/json"
        }


class AuthApp(App):
    _token = os.environ.get('USER_TOKEN')


class AdminApp(App):
    _token = os.environ.get('ADMIN_TOKEN')

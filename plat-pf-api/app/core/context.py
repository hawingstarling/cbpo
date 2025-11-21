import logging

logger = logging.getLogger(__name__)


class AppContext(object):
    """
    A singleton object to scrape META data from HTTP Request Header

    usage:
    jwt_token = AppContext.instance().jwt_token
    client_id = AppContext.instance().client_id
    user_id = AppContext.instance().user_id
    """
    __instance = None

    def __init__(self):
        if AppContext.__instance is not None:
            return
        self._jwt_token = None
        self._client_id = None
        self._user_id = None
        self._user_email = None
        self._request = None

        AppContext.__instance = self

    @staticmethod
    def instance():
        if AppContext.__instance is None:
            return AppContext()
        return AppContext.__instance

    @property
    def jwt_token(self):
        return self._jwt_token

    @jwt_token.setter
    def jwt_token(self, value):
        self._jwt_token = value

    @property
    def client_id(self):
        return self._client_id

    @client_id.setter
    def client_id(self, value):
        self._client_id = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def user_email(self):
        return self._user_email

    @user_email.setter
    def user_email(self, value):
        self._user_email = value

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, value):
        self._request = value

    def clean(self):
        self._jwt_token = None
        self._client_id = None
        self._user_id = None
        self._user_email = None
        self._request = None

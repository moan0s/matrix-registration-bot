import re
import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
import aiohttp
import asyncio


class RegistrationAPI:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = CaseInsensitiveDict()
        self.headers["Authorization"] = f"Bearer {token}"
        self.session = None

    def __str__(self):
        return f"API Connection to {self.base_url}"

    async def ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(self.base_url)

    async def list_tokens(self):
        """
        Gathers a list of all registration tokens

        :return: List of token
        """
        await self.ensure_session()
        async with self.session.get(headers=self.headers) as r:
            return (await r.json())["registration_tokens"]

    @staticmethod
    def token_to_markdown(token_as_dict: dict):
        """
        Converts a token to markdown string

        :param token_as_dict: A dictionary containing the token
            Example: {'token': '8iB~zWiDU1SC0NT3',
                      'uses_allowed': 1,
                      'pending': 0,
                      'completed': 1,
                      'expiry_time': 1642807497388}
        :return: a string in markdown format
        """
        if token_as_dict['uses_allowed'] is None:
            uses_left = "Unlimited"
        else:
            uses_left = token_as_dict['uses_allowed'] - (token_as_dict['completed'] + token_as_dict['pending'])
        if token_as_dict['expiry_time'] is None:
            timestamp = "Does not expire"
        else:
            datetime_obj = datetime.utcfromtimestamp(int(token_as_dict['expiry_time'])/1000)
            timestamp = datetime_obj.strftime("%d.%m.%y %H:%M UTC")
        md = (f"""**Token:** `{token_as_dict['token']}`
        Expires: {timestamp}
        Uses left: {uses_left}
        """)
        return md

    @staticmethod
    def token_to_short_markdown(token_as_dict: dict):
        """
        Converts a token to markdown string

        :param token_as_dict: A dictionary containing the token
            Example: {'token': '8iB~zWiDU1SC0NT3',
                      'uses_allowed': 1,
                      'pending': 0,
                      'completed': 1,
                      'expiry_time': 1642807497388}
        :return: a string of only the token value in markdown format
        """
        md = f"`{token_as_dict['token']}`"
        return md

    @staticmethod
    def valid_token_format(token: str):
        """
        Checks if a string is a valid token.

        The string is checked against a regex pattern. Due to the restricted nature of the token format, the string is
        safe to use when in this format. More information: https://matrix-org.github.io/synapse/latest/usage/administration/admin_api/registration_tokens.html#create-token
        :param token: The token value to check.
        :return:bool: True if the token is in valid format, else false
        """
        if len(token) > 64:
            return False
        pattern = re.compile("[A-Za-z0-9._~-]*")
        match = re.fullmatch(pattern, token)
        return match

    def list_tokens(self):
        """
        Gathers a list of all registration tokens

        :return: List of token
        """
        r = requests.get(self.base_url, headers=self.headers)
        return r.json()["registration_tokens"]

    def get_token(self, token):
        """
        Gets token

        :return: token as dict
        """
        if self.valid_token_format(token):
            r = requests.get(self.base_url + f"/{token}", headers=self.headers)
        else:
            raise TypeError("Token is not a valid format!")
        return r.json()

    def delete_all_token(self):
        """
        Deletes all token

        :return: List of deleted token
        """
        all_tokens = self.list_tokens()
        for token in all_tokens:
            self.delete_token(token["token"])
        return all_tokens

    def delete_token(self, token: str):
        """
        Deletes the given token

        :param token:
        :return: The token that is deleted
        """
        if self.valid_token_format(token):
            r_token = requests.get(self.base_url + f"/{token}", headers=self.headers)
            if r_token.status_code != 200:
                raise FileNotFoundError("Token not found")
            else:
                token = r_token.json()
                r = requests.delete(self.base_url + f"/{token}", headers=self.headers)
                return token
        else:
            raise TypeError("Token is not a valid format!")

    def create_token(self, expiry_days=7):
        """
        Create a token for registering an user

        expire_days:int
            Determines how long the token will be valid (in days)
        """
        expiry_time = int(datetime.timestamp(datetime.now() + timedelta(days=expiry_days)) * 1000)
        data = '{"uses_allowed": 1, "expiry_time": ' + str(expiry_time) + '}'
        r = requests.post(self.base_url + "/new", headers=self.headers, data=data)
        return r.json()

import logging
import re
from datetime import datetime, timedelta
import aiohttp


class RegistrationAPI:
    def __init__(self, base_url: str, api_token: str = "", username: str = "", password: str = "",
                 device_ID: str = "matrix-registration-bot"):
        self.base_url = base_url
        self.api_token = api_token
        self.username = username
        self.password = password
        self.device_ID = device_ID
        self.headers = {"Authorization": f"Bearer {api_token}"}
        self.session = None
        self.registration_token_endpoint = '/_synapse/admin/v1/registration_tokens'

    def __str__(self):
        return f"API Connection to {self.base_url}"

    async def ensure_api_token(self):
        if len(self.api_token) == 0:
            assert len(self.password) > 0 and len(self.username) > 0
            logging.info("Fetching a new API token using user/password combination of the bot")
            self.api_token = await self.get_api_token(self.username, self.password, self.device_ID)
            self.headers = {"Authorization": f"Bearer {self.api_token}"}

    async def ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(self.base_url)

    async def ensure_api(self):
        await self.ensure_session()
        logging.debug(f"Session: {self.session}")
        await self.ensure_api_token()

    async def get_api_token(self, username, password, device_ID):
        logging.debug("Getting api token...")
        await self.ensure_session()
        data = {"identifier": {"type": "m.id.user", "user": f"{username}"},
                "password": f"{password}",
                "type": "m.login.password",
                "device_id": f"{device_ID}"}
        async with self.session.post(f"/_matrix/client/r0/login", json=data) as r:
            self.check_response(r)
            response = await r.json()
            return response["access_token"]

    @staticmethod
    def verbose_response(r):
        return f"The registration api returned `{r.status}: {r.reason}` for {r.method}: {r.url}"

    @staticmethod
    def check_response(r):
        if r.status == 404:
            raise FileNotFoundError("Token not found or API not reachable (404 Not Found)")
        elif r.status == 401:
            raise PermissionError(RegistrationAPI.verbose_response(r) +
                                  f" Check, that the API access token is correct")
        elif r.status != 200:
            raise ConnectionError(RegistrationAPI.verbose_response(r))

    @staticmethod
    def token_to_markdown(token_details: dict):
        """
        Converts a token to markdown string

        :param token_details: A dictionary containing the token
            Example: {'token': '8iB~zWiDU1SC0NT3',
                      'uses_allowed': 1,
                      'pending': 0,
                      'completed': 1,
                      'expiry_time': 1642807497388}
        :return: a string in markdown format
        """
        if token_details['uses_allowed'] is None:
            uses_left = "Unlimited"
        else:
            uses_left = token_details['uses_allowed'] - (token_details['completed'] + token_details['pending'])
        if token_details['expiry_time'] is None:
            timestamp = "Does not expire"
        else:
            datetime_obj = datetime.utcfromtimestamp(int(token_details['expiry_time']) / 1000)
            timestamp = datetime_obj.strftime("%d.%m.%y %H:%M UTC")
        md = (f"""**Token:** `{token_details['token']}`
        Expires: {timestamp}
        Uses left: {uses_left}
        """)
        return md

    @staticmethod
    def token_to_short_markdown(token_details: dict):
        """
        Converts a token to markdown string

        :param token_details: A dictionary containing the token
            Example: {'token': '8iB~zWiDU1SC0NT3',
                      'uses_allowed': 1,
                      'pending': 0,
                      'completed': 1,
                      'expiry_time': 1642807497388}
        :return: a string of only the token value in markdown format
        """
        md = f"`{token_details['token']}`"
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

    async def list_tokens(self):
        """
        Gathers a list of all registration tokens

        :return: List of token_details
        """
        await self.ensure_api()
        async with self.session.get(self.registration_token_endpoint, headers=self.headers) as r:
            try:
                assert r.status == 200
            except AssertionError:
                raise ConnectionError(self.verbose_response(r))
            return (await r.json())["registration_tokens"]

    async def get_token(self, token):
        """
        Gets token

        :return: token_details as dict
        """
        await self.ensure_api()
        if self.valid_token_format(token):
            async with self.session.get(self.registration_token_endpoint + f"/{token}", headers=self.headers) as r:
                self.check_response(r)
                return await r.json()
        else:
            raise TypeError("Token is not a valid format!")

    async def delete_all_token(self):
        """
        Deletes all token

        :return: List of deleted token
        """
        await self.ensure_api()
        all_tokens = await self.list_tokens()
        for token in all_tokens:
            await self.delete_token(token["token"])
        return all_tokens

    async def delete_token(self, token: str):
        """
        Deletes the given token

        :param token:
        :return: The token_details that is deleted as dict
        """
        await self.ensure_api()
        if self.valid_token_format(token):
            r = await self.session.get(f"{self.registration_token_endpoint}/{token}", headers=self.headers)
            self.check_response(r)
            token_details = await r.json()
            async with self.session.delete(f"{self.registration_token_endpoint}/{token}", headers=self.headers) as r:
                self.check_response(r)
                return token_details
        else:
            raise ValueError(f"Token {token} is not a valid format!")

    async def create_token(self, expiry_days=7):
        """
        Create a token for registering a user

        expire_days:int
            Determines how long the token will be valid (in days)
        :return: token_details
        """
        await self.ensure_api()
        expiry_time = int(datetime.timestamp(datetime.now() + timedelta(days=expiry_days)) * 1000)
        data = '{"uses_allowed": 1, "expiry_time": ' + str(expiry_time) + '}'
        async with self.session.post(f"{self.registration_token_endpoint}/new", data=data, headers=self.headers) as r:
            self.check_response(r)
            return await r.json()

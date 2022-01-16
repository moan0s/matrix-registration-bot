import re
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta
import aiohttp


class RegistrationAPI:
    def __init__(self, base_url: str, endpoint: str, api_token: str):
        self.base_url = base_url
        self.endpoint = endpoint
        self.api_token = api_token
        self.headers = CaseInsensitiveDict()
        self.headers["Authorization"] = f"Bearer {api_token}"
        self.session = None

    def __str__(self):
        return f"API Connection to {self.base_url}"

    async def ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(self.base_url)

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
        await self.ensure_session()
        async with self.session.get(self.endpoint, headers=self.headers) as r:
            assert r.status == 200
            return (await r.json())["registration_tokens"]

    async def get_token(self, token):
        """
        Gets token

        :return: token_details as dict
        """
        await self.ensure_session()
        if self.valid_token_format(token):
            async with self.session.get(self.endpoint + f"/{token}", headers=self.headers) as r:
                if r.status != 200:
                    raise FileNotFoundError("Token not found")
                else:
                    return await r.json()
        else:
            raise TypeError("Token is not a valid format!")

    async def delete_all_token(self):
        """
        Deletes all token

        :return: List of deleted token
        """
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
        await self.ensure_session()
        if self.valid_token_format(token):
            r_token = await self.session.get(f"{self.endpoint}/{token}", headers=self.headers)
            if r_token.status != 200:
                print(await r_token.json())
                raise FileNotFoundError(f"{r_token.status} Token not found")
            else:
                token_details = await r_token.json()
                async with self.session.delete(f"{self.endpoint}/{token}", headers=self.headers) as r:
                    return token_details
        else:
            raise ValueError("Token is not a valid format!")

    async def create_token(self, expiry_days=7):
        """
        Create a token for registering a user

        expire_days:int
            Determines how long the token will be valid (in days)
        :return: token_details
        """
        expiry_time = int(datetime.timestamp(datetime.now() + timedelta(days=expiry_days)) * 1000)
        data = '{"uses_allowed": 1, "expiry_time": ' + str(expiry_time) + '}'
        async with self.session.delete(f"{self.endpoint}/new", data=data, headers=self.headers) as r:
            return await r.json()

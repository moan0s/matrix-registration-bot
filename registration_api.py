import requests
from requests.structures import CaseInsensitiveDict
from datetime import datetime, timedelta


class RegistrationAPI():
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        self.headers = CaseInsensitiveDict()
        self.headers["Authorization"] = f"Bearer {token}"

    def __str__(self):
        return f"API Connection to {self.base_url}"

    def list_tokens(self):
        """
        Gathers a list of all registration tokens

        :return: List of token
        """
        r = requests.get(self.base_url, headers=self.headers)
        return r.json()["registration_tokens"]

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
        r = requests.delete(self.base_url + f"/{token}", headers=self.headers)
        print(r)

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

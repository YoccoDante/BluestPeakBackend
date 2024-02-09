import jwt
from time import time
from typing import Union

class TokenController():
    """Class used to work with the tokens, a token is a JWT"""
    SECRET_KEY = "BackendSecretKey"  # Replace with your secret key

    @staticmethod
    def create_token(profile_id:str, range:str) -> str:
        """this method creates and codify a token"""
        payload = {
            "hour": int(time()),
            "_id": profile_id,
            "range": range
        }

        token = jwt.encode(payload, TokenController.SECRET_KEY, algorithm="HS256")

        return token

    @staticmethod
    def validate_token(token:str) -> bool:
        """Returns true if the token is valid."""
        try:
            payload = jwt.decode(token, TokenController.SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return False

        time_passed = int(time()) - payload["hour"]
        if not 0 <= time_passed < 3600:
            return False

        return True

    @staticmethod
    def get_token_id(token:str) -> Union[str, bool]:
        """Returns the decrypted token _id, if not _id, returns false."""
        try:
            payload = jwt.decode(token, TokenController.SECRET_KEY, algorithms=["HS256"])
            return payload["_id"]
        except (jwt.InvalidTokenError, KeyError):
            return False

    @staticmethod
    def get_token_range(token:str) -> Union[str, bool]:
        """This method is used to get the range of the token, if no range, return False."""
        try:
            payload = jwt.decode(token, TokenController.SECRET_KEY, algorithms=["HS256"])
            return payload["range"]
        except (jwt.InvalidTokenError, KeyError):
            return False
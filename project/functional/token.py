from time import time
from typing import Union
from project.functional.crypto import Crypto

class TokenController():
    """Class used to work with the tokens, a token is a long encrypted string"""
    @staticmethod
    def create_token(profile_id:str, range:str) -> str:
        """this method creates and codify a token"""
        hour = f"hour:{int(time())}"
        _id = f"_id:{profile_id}"
        range = f"range:{range}"

        token_elements = [hour, _id, range]
        encrypted_elements = Crypto.encrypt_list(token_elements)

        return "&".join(encrypted_elements)
    
    @staticmethod
    def validate_token(token:str) -> str:
        """Returns true if the token is valid."""
        token_dict = {}
        dependencies = set(["hour","range","_id"])
        token_elements = token.split("&")
        decrypted_elements:list[str] = Crypto.decrypt_list(encrypted_list=token_elements)

        for element in decrypted_elements:
            if ":" not in element:
                return False
            element_name = element[0:element.find(":")]
            element_value = element[element.find(":")+1:len(element)]
            token_dict[element_name] = element_value
        
        for dependency in dependencies:
            if dependency not in token_dict:
                return False

        time_passed = int(time()) - int(token_dict["hour"])
        if not 0 <= time_passed < 3600:
            return False
        
        return True
    
    @staticmethod
    def get_token_id(token:str) -> Union[str,bool]:
        """Returns the decrypted token _id, if not _id, returns false."""
        token_elements = token.split("&")
        decrypted_elements:list[str] = Crypto.decrypt_list(encrypted_list=token_elements)
        for element in decrypted_elements:
            if "_id" in element:
                return element[element.find(":")+1:len(element)]
        
        return False
    
    @staticmethod
    def get_token_range(token:str) -> Union[str,bool]:
        """This method is used to get the range of the token, if no range, return False."""
        token_elements = token.split("&")
        decrypted_elements:list[str] = Crypto.decrypt_list(encrypted_list=token_elements)
        for element in decrypted_elements:
            if "range" in element:
                return element[element.find(":")+1:len(element)]
        
        return False
        
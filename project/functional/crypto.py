from random import shuffle, randint

class Crypto():
    @staticmethod
    def get_encrypted_elements(encrypted_text:str) -> list[str]:
        """Returns a list with the elements of the encrypted text, in order to be used in the decrypt function."""
        num_separator = ["nt","fl","ou","mn"]
        str_separator = ["sr","dc","xt","ln"]
        elements = []
        consonats_index = []
        for i in range(len(encrypted_text)):
            if encrypted_text[i:i+2] in num_separator or encrypted_text[i:i+2] in str_separator:
                consonats_index.append(i+1)

        elements.append(encrypted_text[0:consonats_index[0]+1])
        for i in range(len(consonats_index) -1):
            elements.append(encrypted_text[consonats_index[i]+1:consonats_index[i+1]+1])

        return elements
    
    @staticmethod
    def encrypt(text:str) -> str:
        """Recieves a text to encrypt it, and returns it's encrypted value."""
        new_text = ""
        num_separator = ["nt","fl","ou","mn"]
        str_separator = ["sr","dc","xt","ln"]

        for c in text:
            index = randint(0,3)
            if 48 <= ord(c) <= 57 :
                new_text += f"{ord(c)-(index)}{num_separator[index]}"
            else:
                new_text += f"{ord(c)-(index*10)}{str_separator[index]}"
        return new_text

    @staticmethod
    def encrypt_list(list:list[str]) -> list[str]:
        """Recieves a string list and returns a new list with the encrypted data in diferent order."""
        new_list = []
        for element in list:
            new_list.append(Crypto.encrypt(element))
        shuffle(new_list)
        return new_list
    
    @staticmethod
    def decrypt(encrypted_text:str) -> str:
        """The decrypted text will be returned"""
        num_separator = ["nt","fl","ou","mn"]
        str_separator = ["sr","dc","xt","ln"]
        encrypted_elements = Crypto.get_encrypted_elements(encrypted_text=encrypted_text)
        decrypted_text = ""

        for element in encrypted_elements:
            element_len = len(element)
            if element[element_len-2:element_len] in num_separator:
                for i in range(len(str_separator)):
                    if element[element_len-2:element_len] == num_separator[i]:
                        decrypted_text += chr(int(element[0:element_len-2])+i)
            else:
                for i in range(len(str_separator)):
                    if element[element_len-2:element_len] == str_separator[i]:
                        decrypted_text += chr(int(element[0:element_len-2])+(10*i))

        return decrypted_text

    @staticmethod
    def decrypt_list(encrypted_list:list[str]):
        """Recieves a encrypted string list and returns a new list with it's elements decrypted"""
        decrypted_list = []
        for element in encrypted_list:
            decrypted_list.append(Crypto.decrypt(encrypted_text=element))

        return decrypted_list



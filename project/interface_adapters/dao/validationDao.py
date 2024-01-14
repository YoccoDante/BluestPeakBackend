from project.frameworks_and_drivers.database import db
from project.entities.validation_code import ValidationCode

class ValidationDao:
    @staticmethod
    def save_validation_code(validation_code:ValidationCode):
        validation_codes = db['validation_codes']
        try:
            validation_codes.insert_one(validation_code.__dict__)
        except:
            raise ValueError(f'imposible to save validation code dict')
    
    @staticmethod
    def get_validation_code(email:str, enterprise_id:str) -> ValidationCode:
        validation_codes = db['validation_codes']
        try:
            vc = validation_codes.find_one({'email':email,'enterprise_id':enterprise_id})
            return ValidationCode(
                id=vc['_id'],
                code=vc['code'],
                email=vc['email'],
                timestamp=vc['time_stamp'],
                attempts=vc['attempts']
            )
        except:
            raise ValueError(f'imposible to find validation code with {email} {enterprise_id}')

    @staticmethod
    def delete_validation_code(email:str):
        validation_codes = db['validation_codes']
        try:
            validation_codes.delete_one({'email':email})
        except:
                raise ValueError('imposible to delete validation code')

    @staticmethod
    def update_validation_code_attempts(email, attempts:dict):
        validation_codes = db['validation_codes']
        try:
            validation_codes.update_one({'email':email},{'$set':attempts})
        except:
            raise ValueError('imposible to update validation code')
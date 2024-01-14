from project.interface_adapters.dao.enterpriseDao import EnterpriseDao
from project.entities.enterprise import Enterprise
from project.interface_adapters.dao.userDao import UserDao
from project.functional.crypto import Crypto
from project.functional.token import TokenController
from flask_pymongo import ObjectId
from datetime import datetime
from project.entities.user import User
from project.interface_adapters.dto.userData import UserData

class GetEnterpriseUsageByIdInteractor:
    def __init__(self, enterprise_dao:EnterpriseDao) -> None:
        self.enterprise_dao = enterprise_dao

    def execute(self, enterprise_id, period):
        total_usage_hours = self.enterprise_dao.calculate_total_usage_hours(
            enterprise_id=enterprise_id,
            period=period
        )
        return total_usage_hours
    
class RegisterNewEnterprise:
    def __init__(self, enterprise_dao:EnterpriseDao) -> None:
        self.enterprise_dao = enterprise_dao

    def execute(self, name, email, phone_number):
        if name == '' or email == '' or phone_number == '':
            raise ValueError('empty atributes not allowed')
        
        if self.enterprise_dao.enterprise_exists_by_email(enterprise_email=email):
            raise ValueError('enterprise email already registered')
        
        if self.enterprise_dao.enterprise_exists_by_phone_number(phone_number=phone_number):
            raise ValueError('enterprise phone number already registered')
        
        if self.enterprise_dao.enterprise_exists_by_name(enterprise_name=name):
            raise ValueError('enterprise name already registered')

        new_enterprise = Enterprise(
            email=email,
            name=name,
            phone_number=phone_number
        )

        self.enterprise_dao.add_enterprise(new_enterprise)

class CreateAdminInteractor:
    """Registers a new user to the database and return a new token and the dict of the new user.\n
    user data:{"name","email","password", "last_name",'gender','phone_number'}"""
    def __init__(self, user_dao:UserDao, token_controller:TokenController, crypto:Crypto):
        self.user_dao = user_dao
        self.token_controller = token_controller
        self.crypto = crypto

    def execute(self, user_data, enterprise_id):
        """return a tuple (user_dict, token) with the dict of the new user and it's new token"""
        # Validate the user data...
        dependencies = {"name","email","password", "last_name",'gender','phone_number'}
        for dependency in dependencies:
            if dependency not in user_data or user_data[dependency] == '':
                raise ValueError(f"Missing or empty value for {dependency}")
            
        if user_data['gender'] not in ['male','female','other']:
            raise ValueError(f'Invalid Gender {user_data["gender"]}')
        
        new_range = 'admin'

        new_phone_number = user_data["phone_number"]
        if self.user_dao.user_exists_by_phone_number(
            phone_number=new_phone_number,
            range=new_range,
            enterprise_id=enterprise_id
            ):
            raise ValueError('Contact phone number already exists for this range.')

        new_email = user_data["email"].lower()
        if self.user_dao.user_exists_by_email(
            user_email=new_email,
            enterprise_id=enterprise_id
            ):
            raise ValueError("Email already exists")

        # Create the User object...
        new_id = str(ObjectId())
        new_user = User(
            _id = new_id,
            name=user_data["name"],
            last_name = user_data["last_name"],
            email = new_email,
            password = user_data["password"],
            range=new_range,
            gender=user_data["gender"],
            phone_number=new_phone_number,
            enterprise_id=enterprise_id,
            session_start=datetime.now(),
            last_activity=datetime.now(),
            total_usage_time=0
        )

        # Save the user to the database...
        self.user_dao.add_user(new_user)

        # Generate a token...
        token = self.token_controller.create_token(profile_id=new_user._id,range=new_user.range)
        new_user._id = self.crypto.encrypt(new_id)

        # Return the new user and token...
        return UserData(new_user).__dict__, token
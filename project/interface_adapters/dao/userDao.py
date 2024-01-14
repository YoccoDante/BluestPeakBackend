from project.functional.crypto import Crypto
from project.frameworks_and_drivers.database import db
from project.entities.user import User
from flask_pymongo import ObjectId
import bcrypt

class UserDao():
    @staticmethod
    def get_users(page, page_size, enterprise_id:str, range:str) -> list[dict]:
        """Returns a list with all users from the database."""
        users = db["users"]
        try:
            # Calculate the number of documents to skip
            skip = (page - 1) * page_size
            # Use the skip and limit methods to implement pagination
            query = {"range": range, 'enterprise_id': enterprise_id} if range != 'all' else {'range':{"$ne": "admin"},'enterprise_id':enterprise_id}
            usersRecieved = users.find(query).skip(skip).limit(page_size)
            count = users.count_documents(query)
            total_users = count // page_size if count >= page_size else 1
            user_list = [User(
                _id=Crypto.encrypt(str(ObjectId(user["_id"]))),
                name=user["name"],
                profile_pic=user["profile_pic"],
                gender=user['gender'],
                last_name=user["last_name"],
                email=user["email"],
                stars=user["stars"],
                dept=user["dept"],
                range = user["range"],
                phone_number = user["phone_number"],
                session_start=user['session_start'],
                last_activity=user['last_activity'],
                total_usage_time=user['total_usage_time'],
                enterprise_id=Crypto.encrypt(user['enterprise_id'])
                ).__dict__
                for user in usersRecieved]
            return user_list, total_users
        except:
            raise ValueError('imposible to get users from database')
    
    @staticmethod
    def get_user_by_id(user_id:str, enterprise_id:str) -> User:
        """Returns a User by a given _id."""
        users = db["users"]
        try:
            user = users.find_one({"_id" : user_id, 'enterprise_id':enterprise_id})
            if user is None:
                return None
            user_to_return = User(
                _id=Crypto.encrypt(str(ObjectId(user["_id"]))),
                name=user["name"],
                profile_pic=user["profile_pic"],
                gender=user['gender'],
                last_name=user["last_name"],
                email=user["email"],
                stars=user["stars"],
                dept=user["dept"],
                range = user["range"],
                phone_number = user["phone_number"],
                session_start=user['session_start'],
                last_activity=user['last_activity'],
                total_usage_time=user['total_usage_time'],
                enterprise_id=Crypto.encrypt(user['enterprise_id'])   
            )
            return user_to_return
        except ValueError as e:
            raise e

    @staticmethod
    def get_user_by_email(user_email:str, enterpirse_id:str) -> User:
        """Returns a User by a given _id."""
        users = db["users"]
        try:
            user = users.find_one({"email" : user_email, 'enterprise_id':enterpirse_id})
            user_to_return = User(
                _id=Crypto.encrypt(user['_id']),
                name=user["name"],
                profile_pic=user["profile_pic"],
                gender=user['gender'],
                last_name=user["last_name"],
                email=user["email"],
                stars=user["stars"],
                dept=user["dept"],
                range = user["range"],
                phone_number = user["phone_number"],
                session_start=user['session_start'],
                last_activity=user['last_activity'],
                total_usage_time=user['total_usage_time'],
                enterprise_id=Crypto.encrypt(user['enterprise_id'])
            )    
            return user_to_return
        except ValueError as e:
            raise e

    @staticmethod
    def add_user(user:User) -> None:
        """Adds a new user to the database."""
        users = db["users"]
        # Hash the password before storing it in the database
        try:
            hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
            user.password = hashed_password.decode('utf-8')  # Store the hashed password as a string
            users.insert_one(user.__dict__)
        except ValueError as e:
            raise e
        
    @staticmethod
    def user_exists_by_email(user_email:str, enterprise_id:str) -> bool:
        """Checks if the user exists in the data base by a given email."""
        users = db["users"]
        try:
            if users.count_documents({"email":user_email, 'enterprise_id':enterprise_id}):
                return True
            return False
        except ValueError as e:
            raise e

    @staticmethod
    def user_exists_by_id(user_id:str, enterprise_id:str):
        """Checks if the user exists in the data base by a given _id."""
        users = db["users"]
        try:
            if users.find_one({"_id":user_id, 'enterprise_id':enterprise_id}):
                return True
            return False
        except ValueError as e:
            raise e
    
    @staticmethod
    def user_exists_by_phone_number(phone_number:str, enterprise_id:str, range:str = "user"):
        """Checks if the user exists in the data base by a given phone_number number and a range (user by default), if there's a existing profile with that range and number, returns True."""
        users = db["users"]
        try:
            if users.count_documents({"phone_number":phone_number, "range":range, 'enterprise_id':enterprise_id}):
                return True
            return False
        except ValueError as e:
            raise e

    @staticmethod
    def delete_user(user_id:str, enterprise_id:str):
        """Deletes a user from the database by a given _id."""
        users = db["users"]
        try:
            users.delete_one({"_id":user_id, 'enterprise_id':enterprise_id})
        except ValueError as e:
            raise e
        
    @staticmethod
    def edit_user(user_id:str, atributes:dict, enterprise_id:str) -> None:
        """Edits a User atributes by the atributes dict and a given _id.\n
        atributes dict sintax:\n
        { atribute : new_value, atribute : new_value, ... }"""
        users = db["users"]
        try:
            users.update_one({'_id':user_id, 'enterprise_id':enterprise_id},{'$set':atributes})
        except ValueError as e:
            raise e
        
    @staticmethod
    def validate_user_by_email_and_password(email:str, password:str, enterprise_id:str) -> bool:
        """Checks if a user with the given email and password exists in the database,
        returns a boolean and the user"""
        users = db["users"]
        try:
            user = users.find_one({"email": email, 'enterprise_id':enterprise_id})
            if user is None:
                return False
            # Check the password against the hashed password in the database
            return bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8'))
        except ValueError as e:
            raise e
        
    @staticmethod
    def change_user_password(user_id, new_password, enterprise_id):
        """changes a user password"""
        users = db["users"]
        try:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            new_password = hashed_password.decode('utf-8')  # Store the hashed password as a string
            users.update_one({'user_id': user_id, 'enterprise_id': enterprise_id}, {'$set': {'password': new_password}})
        except:
            raise ValueError('imposible to change user password')
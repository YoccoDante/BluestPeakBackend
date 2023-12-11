from datetime import datetime
from flask_pymongo import ObjectId
from project.entities.user import User
from project.interface_adapters.dto.userData import UserData
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.commentDao import CommentDao
from project.interface_adapters.dao.rateDao import RateDao
from project.interface_adapters.dao.productDao import ProductDao
from project.functional.token import TokenController
from project.functional.crypto import Crypto
from project.functional.image import ImageController

class CreateUserInteractor:
    def __init__(self, user_dao:UserDao, token_controller:TokenController, crypto:Crypto):
        self.user_dao = user_dao
        self.token_controller = token_controller
        self.crypto = crypto

    def execute(self, user_data, enterprise_id):
        # Validate the user data...
        dependencies = {"name","email","password", "last_name",'gender','phone_number','range'}
        for dependency in dependencies:
            if dependency not in user_data or user_data[dependency] == '':
                raise ValueError(f"Missing or empty value for {dependency}")
            
        if user_data['gender'] not in ['male','female','other']:
            raise ValueError(f'Invalid Gender {user_data["gender"]}')

        new_range = user_data["range"]
        if new_range != "host" and new_range != "user":
            raise ValueError("Invalid range")

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
    
class GetUsersInteractor:
    def __init__(self, user_dao:UserDao, rate_dao:RateDao, crypto:Crypto):
        self.user_dao = user_dao
        self.rate_dao = rate_dao
        self.crypto = crypto

    def execute(self, range, page, page_size, enterprise_id) -> list[dict]:
        # Validate the range...
        if range != "user" and range != "host":
            raise ValueError("Invalid range")

        # Get the user data...
        user_dicts = self.user_dao.get_users(range=range, page=page, page_size=page_size, enterprise_id=enterprise_id)

        return user_dicts

class DeleteUserInteractor:
    def __init__(self, product_dao:ProductDao, user_dao:UserDao, rate_dao:RateDao, comment_dao:CommentDao, image_controller:ImageController, token_controller:TokenController):
        self.user_dao = user_dao
        self.rate_dao = rate_dao
        self.comment_dao = comment_dao
        self.image_controller = image_controller
        self.token_controller = token_controller
        self.product_dao = product_dao

    def execute(self, token, enterprise_id):
        user_id = self.token_controller.get_token_id(token)

        if user_id == False:
            raise ValueError("Invalid token")

        if not self.user_dao.user_exists_by_id(
            user_id=user_id,
            enterprise_id=enterprise_id
        ):
            raise ValueError(f"Invalid user {user_id}")

        self.image_controller.delete_images(images_key=user_id)

        self.user_dao.delete_user(
            user_id=user_id,
            enterprise_id=enterprise_id
        )               
        self.rate_dao.delete_many(
            query={
                'rated_id':user_id,
                'enterprise_id':enterprise_id
            }
        )
        self.comment_dao.delete_commentaries(
            commenter_id=user_id,
            enterprise_id=enterprise_id
        )
        self.product_dao.delete_many(
            query={
                'owner':user_id,
            }
        )

class EditUserInteractor:
    def __init__(self, user_dao:UserDao, token_controller:TokenController,) -> None:
        self.user_dao = user_dao
        self.token_controller = token_controller
    
    def execute(self, token, atributes, enterprise_id):
        user_id = self.token_controller.get_token_id(token)

        if 'gender' in atributes and atributes['gender'] not in ['male','female','other']:
            raise ValueError('Invalid Gender')

        if user_id == False:
            raise ValueError("Invalid token")

        if not self.user_dao.user_exists_by_id(
            user_id=user_id,
            enterprise_id=enterprise_id
        ):
            raise ValueError("Invalid user")

        list_of_changes = set(["name","email",'gender','phone_number',"last_name"])
    
        for atribute in atributes:
            if atribute not in list_of_changes:
                raise ValueError("Invalid attribute")

        self.user_dao.edit_user(
            user_id=user_id,
            atributes=atributes,
            enterprise_id=enterprise_id
        )

class EditProfilePicInteractor:
    def __init__(self,token_controller:TokenController, user_dao:UserDao, image_controller:ImageController) -> None:
        self.user_dao = user_dao
        self.image_controller = image_controller
        self.token_controller = token_controller

    def execute(self, token, img, enterprise_id):
        if not self.image_controller.validate_extenstion(file_name=img.filename):
            raise ValueError("image file must be: 'jpg, jpeg, jfif, png'")
        
        user_id = self.token_controller.get_token_id(token=token)

        if user_id == False:
            raise ValueError('invalid user')
        
        user:User = self.user_dao.get_user_by_id(
            user_id=user_id,
            enterprise_id=enterprise_id
        )

        #the url sintax for profiles is: bucket/profile/image_id . extention
        if user.profile_pic == None:
            new_pic_url = self.image_controller.upload_profile_pic(
                enterprise_id=enterprise_id,
                image=img,
                owner_id=user._id
            )
        else:
            image_key = user.profile_pic.rsplit("/",1)[1].lower()
            try:
                self.image_controller.delete_img(img_key=image_key)
                new_pic_url = self.image_controller.upload_profile_pic(
                enterprise_id=enterprise_id,
                image=img,
                owner_id=Crypto.decrypt(user._id)
            )
            except ValueError as e:
                raise e

        self.user_dao.edit_user(
            user_id=user_id,
            atributes={"profile_pic":new_pic_url},
            enterprise_id=enterprise_id
        )
from project.interface_adapters.dto.userData import UserData
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.rateDao import RateDao
from project.functional.token import TokenController

class UserLoginInteractor:
    def __init__(self, user_dao:UserDao, rate_dao:RateDao, token_controller:TokenController):
        self.user_dao = user_dao
        self.rate_dao = rate_dao
        self.token_controller = token_controller

    def execute(self, email, password, enterprise_id):
        if not self.user_dao.validate_user_by_email_and_password(
            email=email,
            password=password,
            enterprise_id=enterprise_id
        ):
            raise ValueError('invalid user')
        
        user = self.user_dao.get_user_by_email(
            user_email=email,
            enterpirse_id=enterprise_id
        )
        user_id = user._id
        user.stars = self.rate_dao.get_target_rate(
            target_id=user_id,
            enterprise_id=enterprise_id
        )
        user_dict = UserData(user).__dict__
        token = self.token_controller.create_token(range=user.range, profile_id=user_id)

        return user_dict, token
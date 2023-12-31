from project.entities.rate import Rate
from project.interface_adapters.dao.rateDao import RateDao
from project.functional.token import TokenController
from project.functional.crypto import Crypto

class RateTargetInteractor:
    def __init__(self, rate_dao:RateDao, token_controller:TokenController, crypto:Crypto):
        self.rate_dao = rate_dao
        self.token_controller = token_controller
        self.crypto = crypto

    def execute(self, token, target_id, rate, enterprise_id):
        rater_id = self.token_controller.get_token_id(token)
        new_rate = Rate(
            rater_id=rater_id,
            target_id=self.crypto.decrypt(target_id),
            rate=rate,
            enterprise_id=enterprise_id
        )

        self.rate_dao.rate_object(new_rate)

class GetRateInteractor:
    def __init__(self, rate_dao:RateDao, crypto:Crypto):
        self.rate_dao = rate_dao
        self.crypto = crypto

    def execute(self, target_id, enterprise_id):
        target_id = self.crypto.decrypt(target_id)
        user_rate = self.rate_dao.get_target_rate(
            target_id=target_id,
            enterprise_id=enterprise_id
        )
        return user_rate
    

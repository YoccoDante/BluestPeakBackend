from project.interface_adapters.dao.snsDao import SnsDao
from project.interface_adapters.dao.verificationDao import VerificationDao
from random import randint

class SendEmailVerificationCodeInteractor:
    """This is not being used yet"""
    def __init__(self, sns_dao:SnsDao, verification_dao:VerificationDao):
        self.sns_dao = sns_dao
        self.verification_dao = verification_dao

    def execute(self, email, verification_topic_arn):
        verification_code = randint(100000, 999999)
        self.verification_dao.store_verification_code(email, verification_code)
        self.sns_dao.publish_message(verification_topic_arn, f"Your verification code is: {verification_code}")

# Similarly for SendPhoneVerificationCodeInteractor...
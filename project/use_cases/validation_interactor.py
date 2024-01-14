import secrets
from project.use_cases.email_interactor import SendEmailInteractor
from project.interface_adapters.dao.validationDao import ValidationDao
from project.entities.validation_code import ValidationCode
from flask_pymongo import ObjectId
from datetime import datetime, timedelta

class SendEmailValidationInteractor:
    def __init__(self, validation_dao:ValidationDao):
        self.validation_dao = validation_dao
        self.send_email_interactor = SendEmailInteractor()

    def execute(self, email):
        #deletes any existing validation code
        self.validation_dao.delete_validation_code(email=email)

        # Generate a validation code
        code = secrets.token_hex(3)
        new_vc_id = str(ObjectId())

        #create new validation code object
        vc = ValidationCode(
            _id= new_vc_id,
            code=code,
            email=email
        )

        # Store the validation code
        try:
            self.validation_dao.save_validation_code(validation_code=vc)
        except ValueError as e:
            raise e

        # Send the validation code to the email address
        self.send_email_interactor.send_email(
            to_address=email,
            from_address='no-reply@bluestpeak.com',  # Replace with your email address
            subject='Your validation code',
            body_text=f'Your validation code is: {code}',
            body_html=f'<p>Your validation code is: {code}</p>'
        )

class ValidateCodeInteractor:
    def __init__(self, validation_dao:ValidationDao) -> None:
        self.validation_dao = validation_dao

    def execute(self, code, email):
        vc:ValidationCode = self.validation_dao.get_validation_code(
            email=email
        )
        if not vc:
            return False

        # Check if it's been more than 5 minutes
        if datetime.now() - vc.timestamp > timedelta(minutes=5):
            self.validation_dao.delete_validation_code(email=email)
            return False

        # Check if the attempts are more than 3
        if vc.attempts > 3:
            self.validation_dao.delete_validation_code(email=email)
            return False

        # Check if the code is correct
        if vc.code != code:
            vc.attempts += 1
            self.validation_dao.update_validation_code_attempts(email=email,attempts=vc.attempts)
            return False

        # If the code is correct, delete it from the database and return True
        self.validation_dao.delete_validation_code(email=email)
        return True
from flask import Blueprint, request, make_response
from project.interface_adapters.dao.verificationDao import VerificationDao

bpverification = Blueprint('vefirication',__name__,url_prefix='/verification')
"""This is not being used yet"""

bpverification.route('/email', methods=['POST'])
def verify_email():
    request_json = request.get_json()
    entered_code = request_json["verification_code"]
    email = request_json["email"]
    stored_code = VerificationDao.get_verification_code(email)
    
    if entered_code == stored_code:
        VerificationDao.mark_as_verified(email)
        return make_response({"msg": "Email verified successfully"}, 200)
    else:
        return make_response({"error": "Invalid verification code"}, 400)

# Similarly for verify_phone...
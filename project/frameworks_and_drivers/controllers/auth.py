from project.interface_adapters.dao.rateDao import RateDao
from project.functional.crypto import Crypto
from project.functional.token import TokenController
from flask import Blueprint, request, make_response
from project.interface_adapters.dao.userDao import UserDao
from project.use_cases.auth_interactor import UserLoginInteractor

#This file is made with security purposes

bpauth = Blueprint("auth", __name__, url_prefix="/auth")

@bpauth.route("/user", methods=["POST"])
def user_login():
    """Requires user_email and user_password from the request"""
    request_json = request.get_json()
    dependencies = ["email","password"]
    enterprise_id = request.headers.get('Enterprise-Id')

    for dependency in dependencies:
        if dependency not in request_json or dependency == "" or dependency == None:
            return make_response({
                "error":"not enough data to log the user in"
            },400)
        
    email = request_json["email"]
    password = request_json["password"]

    interactor = UserLoginInteractor(UserDao, RateDao, TokenController, Crypto)
    try:
        user_dict, token = interactor.execute(
            email=email,
            password=password,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            "error": str(e)
        }, 400)

    return make_response({
        "user": user_dict,
        "token": token
    })
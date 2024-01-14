from flask import Blueprint, make_response, request
from project.use_cases.user_interactor import GetUsersInteractor, DeleteUserInteractor, ChangePasswordinteractor
from project.interface_adapters.dao.rateDao import RateDao
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.productDao import ProductDao
from project.interface_adapters.dao.commentDao import CommentDao
from project.functional.image import ImageController
from project.functional.token import TokenController
from project.functional.crypto import Crypto
from project.frameworks_and_drivers.decorators import required_admin_auth

bpadmin = Blueprint('admin',__name__, url_prefix='/admin')

@bpadmin.route('/user/result', methods=['GET'])
@required_admin_auth
def get_users():
    range = request.args.get('range')
    page = request.args.get('page')
    page_size = request.args.get('page_size')
    enterprise_id = request.headers.get('Enterprise-Id')

    interactor = GetUsersInteractor(
        crypto=Crypto,
        rate_dao=RateDao,
        user_dao=UserDao
    )
    try:
        user_dicts = interactor.execute(
            enterprise_id=enterprise_id,
            page=page,
            page_size=page_size,
            range=range
        )
        return make_response({
            'users':user_dicts
        },200)
    except ValueError as e:
        return make_response({
            'error':f"{e}"
        },400)
    
@bpadmin.route('/user/<string:user_id>', methods=['DELETE'])
@required_admin_auth
def delete_user(user_id):
    enterprise_id = request.headers.get('Enterprise-Id')
    token = request.headers.get('Authorization')
    interactor = DeleteUserInteractor(
        comment_dao=CommentDao,
        image_controller=ImageController,
        product_dao=ProductDao,
        rate_dao=RateDao,
        token_controller=TokenController,
        user_dao=UserDao
    )
    try:
        interactor.execute(
            token=token,
            enterprise_id=enterprise_id,
            user_id=Crypto.decrypt(user_id)
        )
        return make_response({
            'msg':'user deleted sucessfully'
        },200)
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        },400)
    
@bpadmin.route("/user/<string:user_id>", methods=["PUT"])
@required_admin_auth
def change_user_password(user_id):
    user_id = Crypto.decrypt(user_id)
    interactor = ChangePasswordinteractor(UserDao)
    request_json = request.get_json()
    new_password = request_json['new_password']
    enterprise_id = request.headers.get('Enterprise-Id')
    try:
        interactor.execute(
            user_id = user_id,
            new_password=new_password,
            enterprise_id=enterprise_id
        )
        return make_response({
            'msg':'password edited'
        },200)
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        },400)
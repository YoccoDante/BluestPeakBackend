from project.functional.crypto import Crypto
from project.interface_adapters.dao.commentDao import CommentDao
from flask import Blueprint, make_response, request
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.rateDao import RateDao
from project.interface_adapters.dao.productDao import ProductDao
from project.functional.image import ImageController
from project.functional.token import TokenController
from project.use_cases.user_interactor import DeleteUserInteractor,EditUserInteractor,EditProfilePicInteractor,CreateUserInteractor,GetUsersInteractor,ChangePasswordinteractor
from project.frameworks_and_drivers.decorators import required_auth
from flask import current_app

bpuser = Blueprint("user", __name__, url_prefix="/user")

@bpuser.route("/result", methods=["GET"])
def get_users():
    """Returns a list with the info of all the users"""
    current_app.logger.info('trying to get users')
    page = int(request.args.get('page', default=1))
    page_size = int(request.args.get('page_size', default=10))
    range = request.args.get('range', default='user')
    enterprise_id = request.headers.get('Enterprise-Id')

    interactor = GetUsersInteractor(UserDao, RateDao, Crypto)
    try:
        user_dicts, total_users = interactor.execute(range=range, page=page, page_size=page_size, enterprise_id=enterprise_id)
    except ValueError as e:
        return make_response({"error": str(e)}, 400)

    return make_response({
        "users": user_dicts,
        'total':total_users
    }, 200)

#Método para añadir un usuario POST
@bpuser.route("/new", methods=["POST"])
def add_user ():
    """Register a new user and saves it in the database.\n
    Minimun data: 'name','email','password', 'last_name','gender','contact'"""
    request_json = request.get_json()
    enterprise_id = request.headers.get('Enterprise-Id')

    interactor = CreateUserInteractor(UserDao, TokenController, Crypto)
    try:
        user_dict, token = interactor.execute(
            user_data=request_json,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({"error": str(e)}, 400)

    return make_response({
        "user": user_dict,
        "token": token
    },200)

#Método para eliminar un usuario DELETE
@bpuser.route("/", methods=['DELETE'])
@required_auth
def delete_user():
    """The data from the user using this method will be deleted from the database. Only the token must be passed in the request."""
    token = request.headers.get('Authorization')
    enterprise_id = request.headers.get('Enterprise-Id')
    interactor = DeleteUserInteractor(UserDao, RateDao, CommentDao, ImageController, TokenController)
    try:
        interactor.execute(
            token=token,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({"error": str(e)}, 400)

    return make_response({
        "mgs":"user deleted"
    })

#Método para editar datos de un usuario POST
@bpuser.route("/", methods=["PUT"])
@required_auth
def edit_user():
    """Recieves two parameters, the first one is a token, and the second is a 'atributes' dictionary which contains the changes to commit.\n
    Atributes dictionary sintax:\n
    { atribute : value , atribute : value , ...}\n
    valid keys: 'name','email','gender','phone_number','last_name'"""
    request_json = request.get_json()
    token = request.headers.get('Authorization')
    enterprise_id = request.headers.get('Enterprise-Id')

    atributes = request_json["atributes"]

    interactor = EditUserInteractor(UserDao, TokenController)
    try:
        interactor.execute(
            token=token,
            atributes=atributes,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({"error": str(e)}, 400)

    return make_response({
        "msg":"user edited successfuly"
    },200)

@bpuser.route("/profile_pic", methods=["POST"])
@required_auth
def edit_profile_pic():
    """Requires token and the image file with the name img from the request.\n
    Content-Type = Multipart form-data:\n
    token:Text = ...\n
    img:File = ..."""
    if "img" not in request.files:
        return make_response({"error": "img missing"}, 400)

    img = request.files["img"]
    token = request.headers.get('Authorization')
    enterprise_id = request.headers.get('Enterprise-Id')

    try:
        interactor = EditProfilePicInteractor(TokenController, UserDao, ImageController)
        interactor.execute(
            token=token,
            img=img,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        },400)

    return make_response({
        "msg":"profile pic updated"
    })

@bpuser.route('/delete_all_users', methods=['DELETE'])
def delete_all_users():
    enterprise_id = request.headers.get('Enterprise-Id')
    users = UserDao.get_users(
        enterprise_id=enterprise_id,
        page=1,
        page_size=20,
        range='host',
    )
    interactor = DeleteUserInteractor(
        product_dao=ProductDao,
        comment_dao=CommentDao,
        image_controller=ImageController,
        rate_dao=RateDao,
        token_controller=TokenController,
        user_dao=UserDao
    )
    try:
        for user in users:
            token = TokenController.create_token(
                profile_id=Crypto.decrypt(user['_id']),
                range='host'
            )
            interactor.execute(
                token=token,
                enterprise_id=enterprise_id
            )
        return make_response({
            'msg':'done'
        },200)
    except ValueError as e:
        return make_response({
            'error':f"{e}"
        },400)
    
@bpuser.route("/", methods=["PUT"])
@required_auth
def change_user_password():
    token = request.headers.get('Authorization')
    user_id = TokenController.get_token_id(token)
    interactor = ChangePasswordinteractor(UserDao)
    request_json = request.get_json()
    new_password = request_json['new_password']
    try:
        interactor.execute(
            user_id = user_id,
            new_password=new_password
        )
        return make_response({
            'msg':'password edited'
        },200)
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        },400)
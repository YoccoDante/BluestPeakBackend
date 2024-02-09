from flask import Blueprint,make_response,request
from project.interface_adapters.dao.productDao import ProductDao
from project.interface_adapters.dao.rateDao import RateDao
from project.interface_adapters.dao.commentDao import CommentDao
from project.interface_adapters.dao.userDao import UserDao
from project.use_cases.root_interactor import GetProductRootInteractor, GetUserRootInteractor

bproots = Blueprint("root",__name__, url_prefix="/root")

@bproots.route("/product/<string:product_id>", methods=["GET"])
def get_product_root(product_id):
    interactor = GetProductRootInteractor(ProductDao, RateDao, CommentDao, UserDao)
    enterprise_id = request.headers.get('Enterprise-Id')
    try:
        product_data, user_data, comments = interactor.execute(
            product_id=product_id,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        },400)

    return make_response({
        "root":{
            "product":product_data,
            "user":user_data,
            "comments":comments
        }
    },200)

@bproots.route("/user/<string:user_id>", methods=["GET"])
def get_user_root(user_id:str):
    enterprise_id = request.headers.get('Enterprise-Id')
    interactor = GetUserRootInteractor(UserDao, ProductDao, RateDao, CommentDao)
    try:
        user_data, comments, user_products = interactor.execute(
            user_id=user_id,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        },400)

    return make_response({
        "root":{
            "user":user_data,
            "comments":comments,
            "products":user_products
        }
    },200)
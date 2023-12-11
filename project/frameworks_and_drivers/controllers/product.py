import json
from project.functional.crypto import Crypto
from project.interface_adapters.dao.commentDao import CommentDao
from project.functional.token import TokenController
from flask import Blueprint, make_response, request
from project.interface_adapters.dao.productDao import ProductDao
from project.use_cases.product_interactor import AddProductInteractor, GetProductsInteractor, DeleteProductInteractor, GetProductsByOwnerIdInteractor, EditProductInteractor
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.rateDao import RateDao
from project.functional.image import ImageController
from project.frameworks_and_drivers.decorators import required_auth

bpproducts = Blueprint("product", __name__, url_prefix="/product")

@bpproducts.route("/result", methods=["GET"])
def get_products():
    """Returns a list with all the products from the data base."""
    page = int(request.args.get('page', default=1))
    page_size = int(request.args.get('page_size', default=10))
    enterprise_id = request.headers.get('Enterprise-Id')

    interactor = GetProductsInteractor(ProductDao, RateDao, Crypto)
    product_dicts = interactor.execute(
        page=page,
        page_size=page_size,
        enterprice_id=enterprise_id
    )

    return make_response({
        "products": product_dicts
    }, 200)

@bpproducts.route("/<string:user_id>", methods=['GET'])
def get_products_by_owner_id(user_id):
    interactor = GetProductsByOwnerIdInteractor(UserDao, ProductDao, Crypto)
    enterprise_id = request.headers.get('Enterprise-Id')
    try:
        product_dicts = interactor.execute(
            user_id=user_id,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({"error": str(e)}, 400)

    return make_response({
        'products': product_dicts
    })

@bpproducts.route("/new", methods=["POST"])
@required_auth
def add_product():
    """In order to create a new product, the token and the atributes must be passed in te request.
    Request Headers -> Content-Type = Multipart form-data\n
    Request sintax and minimun data:\n
    token:Text = 'token' \n
    imgs:File = '...'\n
    category:Text = '...'\n
    title:Text = '...'\n
    description:Text = '...'\n
    region:Text = '...'\n
    province:Text = '...'\n
    price:Text = '...'"""
    #Validating dependencies
    dependencies = {"stock","category","title","description","region","province","price"}
    for dependency in dependencies:
        #checking text dependencies
        if dependency not in request.form.keys():
            return make_response({
                "error":f"no {dependency} passed"
            })
        #cheking if text dependency is not empty
        if request.form[f"{dependency}"] == None or request.form[f"{dependency}"] == "":
            return make_response({
                "error":f"{dependency} cannot be empty"
            })
    #checking file dependencies
    if "imgs" not in request.files:
        return make_response({
            "error":"no media uploaded"
        })

    #declaring variables
    token = request.headers.get('Authorization')
    imgs = request.files.getlist("imgs")
    category = request.form["category"]
    title = request.form["title"]
    description = request.form["description"]
    region = request.form["region"]
    province = request.form["province"]
    price = request.form["price"]
    stock = int(request.form['stock'])
    enterprise_id = request.headers.get('Enterprise-Id')

    try:
        interactor = AddProductInteractor(UserDao, ProductDao, ImageController, TokenController)
        new_product_data = interactor.execute(
            token=token,
            imgs=imgs,
            category=category,
            title=title,
            description=description,
            region=region,
            province=province,
            price=price,
            stock=stock,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        },400)

    return make_response({
        "new product": new_product_data
    },200)

@bpproducts.route("/", methods=['DELETE'])
@required_auth
def delete_product():
    """In order to delete a product the host token, product _id must be passed in the request."""
    request_json = request.get_json()
    if 'product_id' not in request_json:
        return make_response({
            'error':'missing product_id'
        })

    product_id = Crypto.decrypt(request_json["product_id"])
    token = request.headers.get('Authorization')
    enterprise_id = request.headers.get('Enterprise-Id')

    interactor = DeleteProductInteractor(UserDao, ProductDao, RateDao, CommentDao, ImageController, TokenController)
    try:
        interactor.execute(
            token=token,
            product_id=product_id,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({"error": str(e)}, 400)

    return make_response({
        "mgs":"product deleted"
    })

@bpproducts.route("/", methods=["PUT"])
@required_auth
def edit_product():
    """Recieves two parameters, the first one is a token, and the second is a dictionary named 'atributes' which contains the changes to commit.\n
    changes dictionary sintax:\n
    { atribute : value , atribute : value , ...}\n
    valid keys: 'able','category','description','price','province','region','stars','title'"""
    dependencies = {"stock","category","title","description","region","province","price"}
    for dependency in dependencies:
        #checking text dependencies
        if dependency not in request.form.keys():
            return make_response({
                "error":f"no {dependency} passed"
            })
        #cheking if text dependency is not empty
        if request.form[f"{dependency}"] == None or request.form[f"{dependency}"] == "":
            return make_response({
                "error":f"{dependency} cannot be empty"
            })
    #checking file dependencies
    if "imgs" not in request.files:
        return make_response({
            "error":"no media uploaded"
        })

    #declaring variables
    token = request.headers.get('Authorization')
    new_imgs = request.files.getlist("imgs")
    category = request.form["category"]
    product_id = request.form["product_id"]
    title = request.form["title"]
    description = request.form["description"]
    region = request.form["region"]
    province = request.form["province"]
    price = request.form["price"]
    stock = int(request.form['stock'])
    enterprise_id = request.headers.get('Enterprise-Id')
    atributes = {
        "stock":stock,
        "category":category,
        "title":title,
        "description":description,
        "region":region,
        "province":province,
        "price":price
    }
    
    for dependency in dependencies:
        if dependency not in request.form or dependency == None:
            return make_response({
                'error':f'missing {dependency}'
            },400)
    
    if not TokenController.validate_token(token=token):
        return make_response({
            "error":"invalid token"
        })
    
    if not "host" == TokenController.get_token_range(token):
        return make_response({
            'error':'only host are permitted'
        })
    
    owner_id = TokenController.get_token_id(token=token)
     
    if owner_id == False:
        return make_response({
            'error':'not posible to authenticate'
        },400)

    new_imgs = None
    if "imgs" in request.files:
        new_imgs = request.files.getlist("imgs")

    try:
        interactor = EditProductInteractor(UserDao, ProductDao, ImageController, TokenController)
        interactor.execute(
            token=token,
            product_id=product_id,
            atributes=atributes,
            new_imgs=new_imgs,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        },400)

    return make_response({
        "msg":"product edited succesfully"
    },200)
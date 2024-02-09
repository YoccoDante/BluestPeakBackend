from project.functional.token import TokenController
from project.interface_adapters.dao.commentDao import CommentDao
from flask import Blueprint, request, make_response
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.productDao import ProductDao
from project.use_cases.comment_interactor import GetRootCommentsInteractor, MakeCommentInteractor, DeleteCommentInteractor, EditCommentInteractor
from project.frameworks_and_drivers.decorators import required_auth

bpcomment = Blueprint("comment", __name__, url_prefix="/comment")

@bpcomment.route("/new", methods=["POST"])
@required_auth
def make_comment ():
    """Sets a new commentary in the database. In order to do that, two parameters must be passed:
    The first one is a token, and the second one is a atributes dictionary which contains the data.\n
    Request sintax:\n
    { atribute : value , atribute : value , ... }\n
    Atributes : 'content' , 'root_id
    '"""
    request_json = request.get_json()
    dependencies = {'root_id','content'}
    for dependency in dependencies:
        if dependency not in request_json:
            return make_response({
                'error':f'missing {dependency}'
            },400)

    token = request.headers.get('Authorization')
    enterprise_id = request.headers.get('Enterprise-Id')
    commenter_id = TokenController.get_token_id(token)
    content = request_json['content']
    root_id = request_json['root_id']

    interactor = MakeCommentInteractor(UserDao, ProductDao, CommentDao, TokenController)
    try:
        new_comment = interactor.execute(
            commenter_id=commenter_id,
            enterprise_id=enterprise_id,
            content=content,
            root_id=root_id
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        },400)

    return make_response({
        "msg":"commentary made",
        'new_comment':new_comment.__dict__
    },200)    

@bpcomment.route("/<string:root_id>", methods=["GET"])
def get_root_comments(root_id:str):
    """Returns all the commentaries made to a specific target, the target _id must be passed in the url."""
    interactor = GetRootCommentsInteractor(CommentDao)
    comment_dicts = interactor.execute(root_id)

    return make_response({
        "comments": comment_dicts
    }, 200)

@bpcomment.route("/<string:comment_id>", methods=["DELETE"])
@required_auth
def delete_comment(comment_id):
    token = request.headers.get('Authorization')
    enterprise_id = request.headers.get('Enterprise-Id')

    interactor = DeleteCommentInteractor(CommentDao, TokenController)
    try:
        interactor.execute(
            token=token,
            comment_id=comment_id,
            enterprise_id= enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        },400)

    return make_response({
        "msg":"comment deleted"
    },200)

@bpcomment.route("/<string:comment_id>", methods=["PUT"])
@required_auth
def edit_comment(comment_id):
    request_json = request.get_json()
    token = request.headers.get('Authorization')
    enterprise_id = request.headers.get('Enterprise-Id')

    if "new_content" not in request_json or request_json["new_content"] == "":
        return make_response({
            'error':'missing new content'
        },400)

    new_content = request_json["new_content"]

    interactor = EditCommentInteractor(CommentDao, TokenController)
    try:
        interactor.execute(
            tokem=token,
            comment_id=comment_id,
            new_content=new_content,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        })

    return make_response({
        "msg":"comment edited succesfully"
    },200)
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.commentDao import CommentDao
from project.interface_adapters.dao.productDao import ProductDao
from project.functional.token import TokenController
from project.entities.comment import Comment
from flask_pymongo import ObjectId
from project.functional.crypto import Crypto

class MakeCommentInteractor:
    def __init__(self, user_dao:UserDao, product_dao:ProductDao, comment_dao:CommentDao, token_controller:TokenController, crypto:Crypto):
        self.user_dao = user_dao
        self.product_dao = product_dao
        self.comment_dao = comment_dao
        self.token_controller = token_controller
        self.crypto = crypto

    def execute(self, commenter_id, content, root_id, enterprise_id):
        if not self.user_dao.user_exists_by_id(
            user_id=commenter_id,
            enterprise_id=enterprise_id
        ):
            raise ValueError('invalid commenter')

        if not (self.user_dao.user_exists_by_id(
            user_id=root_id,
            enterprise_id=enterprise_id    
        ) or self.product_dao.product_exists_by_id(
            product_id=root_id,
            enterprise_id=enterprise_id    
        )):
            raise ValueError('invalid root_id')

        user = self.user_dao.get_user_by_id(user_id=commenter_id, enterprise_id=enterprise_id)

        new_comment = Comment(
            _id=str(ObjectId()),
            content=content,
            commenter_id=commenter_id,
            root_id=root_id,
            enterprise_id=enterprise_id
        )

        self.comment_dao.add_comment(new_comment)
        new_comment.commenter_full_name = user.full_name

        return new_comment

class GetRootCommentsInteractor:
    def __init__(self, comment_dao:CommentDao, crypto:Crypto):
        self.comment_dao = comment_dao
        self.crypto = crypto

    def execute(self, root_id, enterprise_id):
        root_id = self.crypto.decrypt(root_id)
        comments = self.comment_dao.get_root_comments(
            root_id=root_id,
            enterprise_id=enterprise_id
        )

        return comments
    
class DeleteCommentInteractor:
    def __init__(self, comment_dao:CommentDao, token_controller:TokenController):
        self.comment_dao = comment_dao
        self.token_controller = token_controller

    def execute(self, token, comment_id, enterprise_id):
        commenter_id = self.token_controller.get_token_id(token)
        self.comment_dao.delete_comment(
            commenter_id=commenter_id,
            comment_id=comment_id,
            enterprise_id=enterprise_id
        )

class EditCommentInteractor:
    def __init__(self, comment_dao:CommentDao, token_controller:TokenController):
        self.comment_dao = comment_dao
        self.token_controller = token_controller

    def execute(self, token, comment_id, new_content, enterprise_id):
        commenter_id = self.token_controller.get_token_id(token)

        self.comment_dao.edit_comment(
            commenter_id=commenter_id,
            comment_id=comment_id,
            new_content=new_content,
            enterprise_id=enterprise_id
        )
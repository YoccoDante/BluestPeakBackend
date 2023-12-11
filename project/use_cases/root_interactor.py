from project.interface_adapters.dto.productData import ProductData
from project.interface_adapters.dto.productData import ProductData
from project.interface_adapters.dto.userData import UserData
from project.interface_adapters.dao.productDao import ProductDao
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.commentDao import CommentDao
from project.interface_adapters.dao.rateDao import RateDao
from project.functional.crypto import Crypto

class GetProductRootInteractor:
    def __init__(self, product_dao:ProductDao, rate_dao:RateDao, comment_dao:CommentDao, user_dao:UserDao, crypto:Crypto):
        self.product_dao = product_dao
        self.rate_dao = rate_dao
        self.comment_dao = comment_dao
        self.user_dao = user_dao
        self.crypto = crypto

    def execute(self, product_id, enterprise_id):
        product_id = self.crypto.decrypt(product_id)
        if not self.product_dao.product_exists_by_id(product_id=product_id, enterprise_id=enterprise_id):
            raise ValueError('invalid product')

        product = self.product_dao.get_product_by_id(
            product_id=product_id,
            enterprise_id=enterprise_id
        )
        product.stars = self.rate_dao.get_target_rate(
            target_id=product_id,
            enterprise_id=enterprise_id
        )
        product_data = ProductData(product).__dict__

        owner_id = self.crypto.decrypt(product.owner)
        user = self.user_dao.get_user_by_id(
            user_id=owner_id,
            enterprise_id=enterprise_id
        )
        user.stars = self.rate_dao.get_target_rate(
            target_id=owner_id,
            enterprise_id=enterprise_id
        )
        user_data = UserData(user).__dict__

        comments = self.comment_dao.get_root_comments(
            root_id=product_id,
            enterprise_id=enterprise_id
        )

        return product_data, user_data, comments
    
class GetUserRootInteractor:
    def __init__(self, user_dao:UserDao, product_dao:ProductDao, rate_dao:RateDao, comment_dao:CommentDao, crypto:Crypto):
        self.user_dao = user_dao
        self.product_dao = product_dao
        self.rate_dao = rate_dao
        self.comment_dao = comment_dao
        self.crypto = crypto

    def execute(self, user_id, enterprise_id):
        user_id = self.crypto.decrypt(user_id)
        if not self.user_dao.user_exists_by_id(
            user_id=user_id,
            enterprise_id=enterprise_id
        ):
            raise ValueError('invalid user')

        user = self.user_dao.get_user_by_id(
            user_id=user_id,
            enterprise_id=enterprise_id
        )
        user.stars = self.rate_dao.get_target_rate(
            target_id=user_id,
            enterprise_id=enterprise_id
        )
        user_data = UserData(user).__dict__

        comments = self.comment_dao.get_root_comments(
            root_id=user_id,
            enterprise_id=enterprise_id
        )

        user_products = []
        if user.range == 'host':
            user_products = self.product_dao.get_products_by_owner(
                owner_id=user_id,
                enterprise_id=enterprise_id
            )

        return user_data, comments, user_products
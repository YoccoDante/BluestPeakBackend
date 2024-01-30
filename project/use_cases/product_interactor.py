from project.interface_adapters.dao.commentDao import CommentDao
from project.functional.crypto import Crypto
from project.functional.token import TokenController
from project.functional.image import ImageController
from project.interface_adapters.dto.productData import ProductData
from project.interface_adapters.dao.productDao import ProductDao
from project.interface_adapters.dao.rateDao import RateDao
from project.functional.crypto import Crypto
from flask_pymongo import ObjectId
from project.entities.product import Product
from project.interface_adapters.dao.userDao import UserDao
from project.interface_adapters.dao.productDao import ProductDao

class GetProductsInteractor:
    def __init__(self, product_dao:ProductDao, rate_dao:RateDao, crypto:Crypto):
        self.product_dao = product_dao
        self.rate_dao = rate_dao
        self.crypto = crypto

    def execute(self, page, page_size, enterprice_id):
        # Get the product data...
        product_dicts, pages = self.product_dao.get_products(
            page=page,
            page_size=page_size,
            enterprise_id=enterprice_id
        )

        return product_dicts, pages
    
class AddProductInteractor:
    def __init__(self, user_dao:UserDao, product_dao:ProductDao, image_controller:ImageController, token_controller:TokenController):
        self.user_dao = user_dao
        self.product_dao = product_dao
        self.image_controller = image_controller
        self.token_controller = token_controller

    def execute(self, token, imgs, category, title, description, region, province, price, enterprise_id, stock=1):
        if not all(self.image_controller.validate_extenstion(img.filename) for img in imgs):
            raise ValueError("One or more files have an invalid extension")

        if not all(self.image_controller.validate_file_size(img) for img in imgs):
            raise ValueError("One or more files are too large")

        owner_id = self.token_controller.get_token_id(token)

        if owner_id == False or not self.user_dao.user_exists_by_id(
            user_id=owner_id,
            enterprise_id=enterprise_id
        ):
            raise ValueError('invalid user')

        new_product_id = str(ObjectId())

        #getting a list with the new urls
        try:
            list_of_urls = self.image_controller.upload_product_images(
                imgs=imgs,
                owner_id=owner_id,
                new_product_id=new_product_id,
                enterprise_id=enterprise_id
            )
        except Exception as e:
            raise ValueError(f"Failed to upload images: {e}")

        #creating a new product object
        new_product = Product(
            _id = Crypto.encrypt(new_product_id),
            category = category,
            title = title,
            imgs = list_of_urls,
            description = description,
            region = region,
            province = province,
            price = price,
            owner = owner_id,
            enterprise_id=enterprise_id,
            stock=stock
        )

        #necesary dao methods to create the and storage the product in product in the data base and cloud storage
        self.product_dao.add_product(new_product)

        return ProductData(new_product).__dict__
    
class GetProductsByOwnerIdInteractor:
    def __init__(self, user_dao:UserDao, product_dao:ProductDao, crypto:Crypto):
        self.user_dao = user_dao
        self.product_dao = product_dao
        self.crypto = crypto

    def execute(self, user_id, enterprise_id, page, page_size):
        user_id = self.crypto.decrypt(user_id)
        if not self.user_dao.user_exists_by_id(
            user_id=user_id,
            enterprise_id=enterprise_id
        ):
            raise ValueError("Invalid user")

        products = self.product_dao.get_products_by_owner(
            owner_id=user_id,
            enterprise_id=enterprise_id,
            page=page,
            page_size=page_size
        )

        return products
    
class DeleteProductInteractor:
    def __init__(self, user_dao:UserDao, product_dao:ProductDao, rate_dao:RateDao, comment_dao:CommentDao, image_controller:ImageController, token_controller:TokenController):
        self.user_dao = user_dao
        self.product_dao = product_dao
        self.rate_dao = rate_dao
        self.comment_dao = comment_dao
        self.image_controller = image_controller
        self.token_controller = token_controller

    def execute(self, token, product_id, enterprise_id):
        owner_id = self.token_controller.get_token_id(token)

        if owner_id == False:
            raise ValueError('invalid user')

        if not self.product_dao.product_belongs_to_owner(
            product_id=product_id,
            owner_id=owner_id,
            enterprise_id=enterprise_id
        ):
            raise ValueError('invalid product')

        product = self.product_dao.get_product_by_id(
            product_id=product_id,
            enterprise_id=enterprise_id
        )
        if product.imgs != []:
            self.image_controller.delete_images(images_key=product_id)

        self.product_dao.delete_product(
            product_id=product_id,
            enterprise_id=enterprise_id
        )
        self.rate_dao.delete_rated_object(
            rated_id=product_id,
            enterprise_id=enterprise_id
        )
        self.comment_dao.delete_root_commentaries(
            root_id=product_id,
            enterprise_id=enterprise_id
        )

class EditProductInteractor:
    def __init__(self, user_dao:UserDao, product_dao:ProductDao, image_controller:ImageController, token_controller:TokenController):
        self.user_dao = user_dao
        self.product_dao = product_dao
        self.image_controller = image_controller
        self.token_controller = token_controller

    def execute(self, token, product_id, atributes, enterprise_id, new_imgs=None):
        owner_id = self.token_controller.get_token_id(token)

        if owner_id == False:
            raise ValueError('invalid user')

        if not self.product_dao.product_belongs_to_owner(
            product_id=product_id,
            owner_id=owner_id,
            enterprise_id=enterprise_id    
        ):
            raise ValueError('invalid product')

        if new_imgs:
            if not all(self.image_controller.validate_extenstion(img.filename) for img in new_imgs):
                raise ValueError("One or more files have an invalid extension")
            if not all(self.image_controller.validate_file_size(img) for img in new_imgs):
                raise ValueError("One or more files are too large")

            # Delete old images and upload new ones
            product:Product = self.product_dao.get_product_by_id(
                product_id=product_id,
                enterprise_id=enterprise_id
            )
            if product.imgs != []:
                self.image_controller.delete_images(images_key=product_id)

            list_of_urls = self.image_controller.upload_product_images(
                imgs=new_imgs,
                owner_id=owner_id,
                new_product_id=product_id
            )
            atributes["imgs"] = list_of_urls

        self.product_dao.edit_product(
            product_id=product_id,
            atributes=atributes,
            enterprise_id=enterprise_id
        )
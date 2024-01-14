from project.frameworks_and_drivers.database import db
from project.functional.crypto import Crypto
from project.entities.product import Product
from flask_pymongo import ObjectId
from project.interface_adapters.dao.rateDao import RateDao
from project.functional.image import ImageController

class ProductDao():
    @staticmethod
    def get_products(enterprise_id:str, page:int=1, page_size:int=10) -> list[dict]:
        """this method returns a paginated list of all the products data from a enterprise"""
        products = db["products"]
        # Calculate the number of documents to skip
        skip = (page - 1) * page_size
        count = products.count_documents({'enterprise_id':enterprise_id})
        total_products = count // page_size if count >= page_size else 1
        # Use the skip and limit methods to implement pagination
        try:
            productsRecieved = products.find({'able':True, 'enterprise_id':enterprise_id}).skip(skip).limit(page_size)

            product_list = [
                Product(
                    _id = Crypto.encrypt(str(ObjectId(product["_id"]))),
                    category=product["category"],
                    title=product["title"],
                    imgs=product["imgs"],
                    description=product["description"],
                    region=product["region"],
                    province=product["province"],
                    price=product["price"],
                    able = product["able"],
                    owner = Crypto.encrypt(product["owner"]),
                    stars = RateDao.get_target_rate(product['_id'], enterprise_id=product['enterprise_id']),
                    stock=product['stock'],
                    enterprise_id=product['enterprise_id']
                ).__dict__ for product in productsRecieved]
            return product_list, total_products
        except ValueError as e:
            raise e

    @staticmethod
    def get_product_by_id(product_id:str, enterprise_id:str) -> Product:
        """in order to get a specific product, the _id must be passed"""
        products = db["products"]
        try:
            product = products.find_one({"_id" : product_id, 'enterprise_id':enterprise_id})   
            product_to_return = Product(
                _id = Crypto.encrypt(product["_id"]),
                category=product["category"],
                title=product["title"],
                imgs=product["imgs"],
                description=product["description"],
                region=product["region"],
                province=product["province"],
                price=product["price"],
                able = product["able"],
                owner = Crypto.encrypt(product["owner"]),
                stock=product['stock'],
                    enterprise_id=product['enterprise_id']
            )
            return product_to_return
        except ValueError as e:
            raise e
        
    @staticmethod
    def product_belongs_to_owner(product_id:str, owner_id:str, enterprise_id:str) -> bool:
        """this method checks if the product (product_id) belongs to a customer (owner_id)"""
        products = db["products"]
        try:
            if products.count_documents({"_id":product_id,"owner_id":owner_id, 'enterprise_id':enterprise_id}):
                return True
            return True
        except ValueError as e:
            raise e

    @staticmethod
    def add_product(product: Product) -> None:
        """in order to save a product in the database, a product object must be passed"""
        products = db["products"]
        try:
            product_dict = product.__dict__
            products.insert_one(product_dict)
        except ValueError as e:
            raise e
        
    @staticmethod
    def delete_product(product_id:str, enterprise_id:str) -> None:
        """in order to delete a product, it's _id must be passed"""
        products = db["products"]
        try:
            products.delete_one({"_id":product_id, 'enterprise_id':enterprise_id})
        except ValueError as e:
            raise e
        
    @staticmethod
    def edit_product(product_id:str, atributes:dict, enterprise_id:str) -> None:
        """in order to edit a product atribute, a dictionary with the changes must be passed.\n
        Atributes to set: ['title','category','description','region','province','price','able', 'imgs']\n
        It's not necessary to pass all the atributes in the atributes dict\n
        Atributes sintax:\n
        { 'title' : 'new_title', 'province' : 'new_province', etc...}"""
        products = db["products"]
        try:
            for atribute, value in atributes.items():
                if atribute == 'imgs':
                    # Handle image updates
                    old_product = products.find_one({"_id": product_id, 'enterprise_id':enterprise_id})
                    old_imgs = old_product['imgs']
                    # Delete old images and upload new ones
                    value = ImageController.update_images(old_imgs, value, old_product['owner'], product_id)
                products.update_one({"_id": product_id},
                {"$set": {
                    atribute: value
                }})
        except ValueError as e:
            raise e
        
    @staticmethod
    def product_exists_by_id(product_id:str, enterprise_id:str) -> bool:
        products = db["products"]
        try:
            if products.find_one({"_id":product_id, 'enterprise_id':enterprise_id}):
                return True
            return False
        except:
            raise ValueError(f'no such product with _id: {product_id}')
    
    @staticmethod
    def get_products_by_owner(owner_id:str, enterprise_id:str) -> list[Product]:
        """Returns a list of product objects by a given customer_id."""
        products = db["products"]
        try:
            productsRecieved = products.find({"owner":owner_id,'enterprise_id':enterprise_id})
            product_list = [Product(
                _id=Crypto.encrypt(product["_id"]),
                title=product["title"],
                category=product["category"],
                imgs=product["imgs"],
                description=product["description"],
                region=product["region"],
                province=product["province"],
                price=product["price"],
                able=product["able"],
                owner=Crypto.encrypt(product["owner"]),
                stock=product['stock'],
                enterprise_id=product['enterprise_id']
            ).__dict__
            for product in productsRecieved]

            return product_list
        except:
            raise ValueError('no such product or owner')
    
    @staticmethod
    def delete_many(query:dict):
        products = db['products']
        try:
            products.delete_many(query)
        except ValueError as e:
            raise e
        
    @staticmethod
    def count_products(owner_id:str):
        products = db['products']
        try:
            return products.count_documents({'owner_id':owner_id})
        except:
            raise ValueError('imposible to count owner products')
from project.entities.product import Product

class ProductData():
    def __init__(self, Product: Product):
        if Product._id != None:
            self._id:str = Product._id
        self.category:str = Product.category
        self.title:str = Product.title
        self.imgs:list = Product.imgs
        self.description:str = Product.description
        self.region:str = Product.region
        self.province:str = Product.province
        self.price:float = Product.price
        self.able:bool = Product.able
        self.stars:float = Product.stars
        self.stock:int = Product.stock
        self.enterprice_id:str = Product.enterprise_id
class Product():
    def __init__(self, title:str, category:str, description:str, region:str, province:str, price:float, enterprise_id:str, _id:str = None, able:bool=True, owner:str=None, stars:float=0, imgs:list=[], stock:int=1):
        self._id:str = _id
        self.title:str = title #conmandatory
        self.category:str = category #conmandatory
        self.imgs:list = imgs #conmandatory
        self.description:str = description #conmandatory
        self.region:str = region #conmandatory
        self.province:str = province #conmandatory
        self.price:float = price #conmandatory
        self.enterprise_id = enterprise_id #conmandatory
        self.stock = stock
        self.able:bool = able
        self.owner:str = owner
        self.stars:float = stars
from pymongo import MongoClient
from env import MONGO_URI

MONGO_URI = MONGO_URI


class MongoConnection:
    _instance = None

    @staticmethod
    def get_instance():
        if MongoConnection._instance is None:
            MongoConnection()
        return MongoConnection._instance

    def __init__(self):
        if MongoConnection._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            try:
                client = MongoClient(MONGO_URI)
                self.db = client["dbb_usuarios"]
                MongoConnection._instance = self
            except ConnectionRefusedError:
                raise ValueError("imposible to connect with dbb")

db = MongoConnection.get_instance().db
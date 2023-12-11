from project.frameworks_and_drivers.database import db
from project.entities.rate import Rate

class RateDao():
    @staticmethod
    def get_target_rate(target_id:str, enterprise_id:str) -> float:
        """In order to get the target rate, the target_id must be passed,
        and the rate is returned with one decimal as maximun"""
        rating = db["rate"]
        try:
            data = rating.find({"target_id":target_id, 'enterprise_id':enterprise_id})
            votes = [vote['rate'] for vote in data]
            average = (sum(votes) / len(votes)) if len(votes) != 0 else 0
            return round(average, 1)
        except ValueError as e:
            raise e

    @staticmethod
    def rate_object(rate:Rate):
        """This method must be use when rating a object [product, user, costumer]\n
        Target_id is the _id of the object being rated.\n
        Rater_id is the _id of the person who qualifies the target\n
        Rate is te quantity of stars passed"""
        rating = db["rate"]
        try:
            rating.update_one(
            {"rater_id": rate.rater_id, "target_id": rate.target_id, 'enterprise_id':rate.enterprise_id},
            {"$set": {"rate": rate.rate}},
            upsert=True
            )
        except ValueError as e:
            raise e
        
    @staticmethod
    def delete_rated_object(rated_id:str, enterprise_id:str) -> None:
        """In order to delete a rated object from the database, it's _id must be passed"""
        rating = db["rate"]
        try:
            rating.delete_many({"rated_id":rated_id, 'enterprise_id':enterprise_id})
        except ValueError as e:
            raise e

    @staticmethod
    def delete_many(query:dict):
        rating = db["rate"]
        try:
            rating.delete_many(query)
        except ValueError as e:
            raise e
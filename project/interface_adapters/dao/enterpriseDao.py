from datetime import datetime
from project.entities.enterprise import Enterprise
from project.frameworks_and_drivers.database import db

class EnterpriseDao:
    @staticmethod
    def get_enterprise_by_id(enterprise_id:str) -> Enterprise:
        enterprises = db['enterprises']
        try:
            enterprise = enterprises.find_one({'_id':enterprise_id})
            if enterprise is None:
                raise ValueError('Enterprise not found')
        except Exception as e:
            raise ValueError(f"Failed to get enterprise: {e}")

        return Enterprise(
            _id = enterprise['_id'],
            name=enterprise['name'],
            paid=enterprise['paid'],
            total_usage_time=enterprise['total_usage_time'],
            total_users=enterprise['total_users']
        )

    @staticmethod
    def add_enterprise(enterprise:Enterprise):
        enterprises = db['enterprises']
        if not enterprise.name or not isinstance(enterprise.name, str):
            raise ValueError('Invalid enterprise name')
        try:
            enterprises.insert_one(enterprise.__dict__)
        except Exception as e:
            raise ValueError(f"Failed to add enterprise: {e}")

    @staticmethod
    def update_enterprise(enterprise_id:str, attributes:dict):
        enterprises = db['enterprises']
        try:
            enterprises.update_one({'_id':enterprise_id}, {'$set':attributes})
        except Exception as e:
            raise ValueError(f"Failed to update enterprise: {e}")

    @staticmethod
    def delete_enterprise(enterprise_id):
        enterprises = db['enterprises']
        try:
            enterprises.delete_one({'_id':enterprise_id})
        except Exception as e:
            raise ValueError(f"Failed to delete enterprise: {e}")

    @staticmethod
    def get_unpaid_enterprises():
        enterprises = db['enterprises']
        try:
            unpaid = enterprises.find({'paid': False})
        except Exception as e:
            raise ValueError(f"Failed to get unpaid enterprises: {e}")
        
        return [Enterprise(**enterprise) for enterprise in unpaid]

    @staticmethod
    def enterprise_has_paid(enterprise_id:str):
        enterprises = db['enterprises']
        try:
            enterprise = enterprises.find_one({'_id':enterprise_id})
            if enterprise is None:
                raise ValueError(f"No enterprise found with ID {enterprise_id}")
            return enterprise['paid']
        except ValueError as e:
            raise e
        
    @staticmethod
    def calculate_total_usage_hours(enterprise_id:str, period:str):
        # Get all logs for the given enterprise ID
        logs = db['request_logs'].find({'enterprise_id': enterprise_id, 'period':period})
        try:
            # Calculate the total usage
            total_usage = sum(log['duration'] for log in logs)
        except ValueError as e:
            raise e
        
        return total_usage / 3600
    
    @staticmethod
    def enterprise_exists_by_email(enterprise_email:str):
        enterprises = db['enterprises']
        if enterprises.count_documents({'email':enterprise_email}):
            return True
        return False
    
    @staticmethod
    def enterprise_exists_by_phone_number(phone_number:str):
        enterprises = db['enterprises']
        if enterprises.count_documents({'phone_number':phone_number}):
            return True
        return False
    
    @staticmethod
    def enterprise_exists_by_name(enterprise_name:str):
        enterprises = db['enterprises']
        if enterprises.count_documents({'enterprise_name':enterprise_name}):
            return True
        return False

    @staticmethod
    def mark_as_paid(enterprise_id):
        enterprises = db['enterprises']
        enterprises.update_one({'_id': enterprise_id}, {'$set': {'paid': True}})
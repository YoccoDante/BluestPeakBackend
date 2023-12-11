from project.interface_adapters.dao.enterpriseDao import EnterpriseDao
from project.entities.enterprise import Enterprise

class GetEnterpriseUsageByIdInteractor:
    def __init__(self, enterprise_dao:EnterpriseDao) -> None:
        self.enterprise_dao = enterprise_dao

    def execute(self, enterprise_id, period):
        total_usage_hours = self.enterprise_dao.calculate_total_usage_hours(
            enterprise_id=enterprise_id,
            period=period
        )
        return total_usage_hours
    
class RegisterNewEnterprise:
    def __init__(self, enterprise_dao:EnterpriseDao) -> None:
        self.enterprise_dao = enterprise_dao

    def execute(self, name, email, phone_number):
        if name == '' or email == '' or phone_number == '':
            raise ValueError('empty atributes not allowed')
        
        if self.enterprise_dao.enterprise_exists_by_email(enterprise_email=email):
            raise ValueError('enterprise email already registered')
        
        if self.enterprise_dao.enterprise_exists_by_phone_number(phone_number=phone_number):
            raise ValueError('enterprise phone number already registered')
        
        if self.enterprise_dao.enterprise_exists_by_name(enterprise_name=name):
            raise ValueError('enterprise name already registered')

        new_enterprise = Enterprise(
            email=email,
            name=name,
            phone_number=phone_number
        )

        self.enterprise_dao.add_enterprise(new_enterprise)
from flask import Blueprint, make_response, request
from project.use_cases.enterprise_interactor import GetEnterpriseUsageByIdInteractor, RegisterNewEnterprise, CreateAdminInteractor
from project.interface_adapters.dao.enterpriseDao import EnterpriseDao
from project.functional.token import TokenController
from project.interface_adapters.dao.userDao import UserDao

bpenterprise = Blueprint('enterprise',__name__,url_prefix='/enterprise')

@bpenterprise.route('/usage', methods=['GET'])
def get_enterprise_usage_by_id():
    enterprise_id = request.headers.get('Enterprise-Id')
    interactor = GetEnterpriseUsageByIdInteractor(EnterpriseDao)
    period = request.args.get('period')
    try:
        total_usage_hours = interactor.execute(
            enterprise_id=enterprise_id,
            period=period
        )
    except ValueError as e:
        raise e
    
    return make_response({
        "total_usage_hours": total_usage_hours
    }, 200)

@bpenterprise.route('/new')
def register_enterprise():
    request_json = request.get_json()
    dependencies = {'name','email','phone_number'}
    for dependency in dependencies:
        if dependency not in request_json or request_json[dependency] is None:
            return make_response({
                'error':f'not enough data, missing {dependency}'
            },400)

    enterprise_interactor = RegisterNewEnterprise(enterprise_dao=EnterpriseDao)
    try:
        enterprise_interactor.execute(
            email=request_json['email'],
            name=request_json['name'],
            phone_number=request_json['phone_number']
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        }, 400)
    
@bpenterprise.route('/admin', methods=['POST'])
def create_admin():
    enterprise_id = request.headers.get('Enterprise-Id')
    request_json = request.get_json()
    user_data = {
        "name":request_json["name"],
        "email":request_json["email"],
        "password":request_json["password"],
        "last_name":request_json["last_name"],
        "gender":request_json['gender'],
        "phone_number":request_json['phone_number']
    }
    interactor = CreateAdminInteractor(
        token_controller=TokenController,
        user_dao=UserDao
    )
    try:
        user_dict, token = interactor.execute(
            enterprise_id=enterprise_id,
            user_data=user_data
        )
        return make_response({
            'user':user_dict,
            'token':token
        },200)
    
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        },400)
from flask import Blueprint, make_response, request
from project.use_cases.enterprise_interactor import GetEnterpriseUsageByIdInteractor, RegisterNewEnterprise
from project.interface_adapters.dao.enterpriseDao import EnterpriseDao

bpenterprise = Blueprint('enterprise',__name__,url_prefix='/enterprise')

@bpenterprise.route('/usage', methods=['GET'])
def get_enterprise_usage_by_id():
    enterprise_id = request.headers.get('Enterprise-Id')
    interactor = GetEnterpriseUsageByIdInteractor(EnterpriseDao)
    period = request.args.get('period')
    total_usage_hours = interactor.execute(enterprise_id, period=period)
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
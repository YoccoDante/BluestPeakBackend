from flask import Blueprint, request, make_response
from project.interface_adapters.dao.enterpriseDao import EnterpriseDao
from project.use_cases.ipn_interactor import VerifyIpnInteractor

bppayment = Blueprint('payment',__name__, url_prefix='/payment')

@bppayment.route('/ipn-listener', methods=['POST'])
def ipn_listener():
    ipn_message = request.form.to_dict()
    enterprise_id = request.headers.get('Enterprise-Id')
    interactor = VerifyIpnInteractor(
        enterprise_dao=EnterpriseDao,
    )
    try:
        interactor.execute(
            enterprise_id=enterprise_id,
            ipn_message=ipn_message
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        },400)
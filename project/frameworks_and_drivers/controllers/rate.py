from project.functional.token import TokenController
from flask import Blueprint, make_response, request
from project.interface_adapters.dao.rateDao import RateDao
from project.use_cases.rate_interactor import GetRateInteractor, RateTargetInteractor
from project.frameworks_and_drivers.decorators import required_auth

bprate = Blueprint("rate", __name__, url_prefix="/rate")
        
@bprate.route("/", methods=["POST"])
@required_auth
def rate_target():
    """In order to rate a target, two parameters must be passed in the request: The first one is a token, and the decond is a atributes dictionary.\n
    Request sintax: { token : 'token' , atributes : { atribute : 'value' , atribute : 'value' , ... }}\n
    Atributes permited: [ 'rate:int' , 'target_id:str' ]
    Products can be rated by users only\n
    Users can be rated by customers only\n
    Customers can be rated by users only"""
    request_json = request.get_json()
    dependencies = set(['target_id','rate'])
    
    for dependency in dependencies:
        if dependency not in request_json:
            return make_response({
                'error':f'missing {dependency}'
            },400)

    token = request.headers.get('Authorization')
    target_id = request_json['target_id']
    rate = request_json['rate']
    enterprise_id =request.headers.get('Enterprise-Id')

    interactor = RateTargetInteractor(RateDao, TokenController)
    try:
        interactor.execute(
            token=token,
            target_id=target_id,
            rate=rate,
            enterprise_id=enterprise_id
        )
    except ValueError as e:
        return make_response({
            'error':str(e)
        },400)

    return make_response({
        "msg":"target rated"
    },200)    

@bprate.route("/<string:target_id>", methods=["GET"])
def get_rate(target_id:str):
    """In order to get the rate of a specific target, it's _id must be passed in the url."""
    interactor = GetRateInteractor(RateDao)
    enterprise_id = request.headers.get('Enterprise-Id')
    user_rate = interactor.execute(target_id, enterprise_id)

    return make_response({
        "rate": user_rate
    },200)
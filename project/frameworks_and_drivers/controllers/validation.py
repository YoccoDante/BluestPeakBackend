from flask import Blueprint, make_response, request
from project.use_cases.validation_interactor import SendEmailValidationInteractor, ValidateCodeInteractor
from project.interface_adapters.dao.validationDao import ValidationDao

bpvalidation = Blueprint('validation', __name__, url_prefix='/validation')

@bpvalidation.route('/new', methods=['POST'])
def create_new_validation_code():
    request_json = request.get_json()
    enterprise_id = request.headers.get('Enterprise-Id')
    email = request_json['email']
    interactor = SendEmailValidationInteractor(ValidationDao)
    try:
        interactor.execute(
            email=email
        )
    except ValueError as e:
        return make_response({
            'error':f'{e}'
        })

    return make_response({
        'msg':'code generated successfully',
    })
    
@bpvalidation.route('/', methods=['POST'])
def validate_code():
    request_json = request.get_json()
    code = request_json['code']
    email = request_json['email']
    interactor = ValidateCodeInteractor(validation_dao=ValidationDao)

    try:
        result = interactor.execute(
            code=code,
            email=email
        )
    except ValueError as e:
        return make_response({
            'error':f'{e}',
            'success':False
        })
    
    return make_response({
        'msg':'code checked',
        'success':result
    })
    


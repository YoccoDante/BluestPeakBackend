from functools import wraps
from flask import request, make_response
from project.functional.token import TokenController

def required_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method != 'OPTIONS':
            token = request.headers.get("Authorization")
            if token is None:
                return make_response({"error": "Missing Authorization header"}, 400)
            if not TokenController.validate_token(token):
                return make_response({'error':'Invalid token'}, 401)
        return f(*args, **kwargs)
    return decorated
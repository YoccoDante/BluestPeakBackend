from flask import Flask, request, make_response, g
from project.frameworks_and_drivers.controllers.rate import bprate as rate
from project.frameworks_and_drivers.controllers.user import bpuser as users
from project.frameworks_and_drivers.controllers.product import bpproducts as product
from project.frameworks_and_drivers.controllers.comment import bpcomment as comment
from project.frameworks_and_drivers.controllers.root import bproots as root
from project.frameworks_and_drivers.controllers.auth import bpauth as auth
from project.frameworks_and_drivers.controllers.enterprise import bpenterprise as enterprise
from project.frameworks_and_drivers.controllers.validation import bpvalidation as validation
from project.frameworks_and_drivers.controllers.admin import bpadmin as admin
from project.frameworks_and_drivers.database import db
from project.interface_adapters.dao.userDao import UserDao
from project.functional.token import TokenController
from project.interface_adapters.dao.enterpriseDao import EnterpriseDao
from flask_cors import CORS
import datetime

def create_app():
    app = Flask(__name__)
    CORS(app)   
    app.register_blueprint(rate)
    app.register_blueprint(users)
    app.register_blueprint(product)
    app.register_blueprint(comment)
    app.register_blueprint(root)
    app.register_blueprint(auth)
    app.register_blueprint(enterprise)
    app.register_blueprint(validation)
    app.register_blueprint(admin)

    @app.before_request
    def before_request():
        g.start_time = datetime.datetime.now()
        if request.path in ['/enterprise/new', '/validation/','/validation/new'] and request.method == 'POST':
            return
        if request.method == 'OPTIONS':
            return make_response({
                'msg':'ok'
            },200)
        enterprise_id = request.headers.get('Enterprise-Id')
        if enterprise_id is None:
            return make_response({
                'error':'Missing header Enterprise-Id'
            },400)
        # Update user's last activity and session start
        token = request.headers.get('Authorization')  # replace with how you get the token
        if token:
            try:
                user_id = TokenController.get_token_id(token)
                user = UserDao.get_user_by_id(
                    user_id=user_id,
                    enterprise_id=enterprise_id
                )
                now = datetime.datetime.now()
                if now - user.last_activity > datetime.timedelta(minutes=30):
                    # If the user has been inactive for more than 30 minutes, start a new session
                    user.session_start = now
                user.last_activity = now
                UserDao.edit_user(
                    user_id=user_id,
                    atributes={
                        'session_start':user.session_start,
                        'last_activity':user.last_activity
                    },
                    enterprise_id=enterprise_id
                )
            except Exception as e:
                return make_response({
                    'error':f"Error updating user activity: {e}"
                },400) 

    @app.after_request
    def after_request(response):
        if request.path in ['/enterprise/new', '/validation/','/validation/new'] and request.method == 'POST':
            return
        end_time = datetime.datetime.now()
        duration = (end_time - g.start_time).total_seconds()

        # Log the request with the enterprise Id, the endpoint, the method, the duration, the period, and the current timestamp
        enterprise_id = request.headers.get('Enterprise-Id')
        if request.method != 'OPTIONS' and enterprise_id is None:
            return make_response({
                'error':'missing header: Enterprise-Id'
            }, 400)

        if enterprise_id:
            if not EnterpriseDao.enterprise_has_paid(enterprise_id):
                return make_response({
                    'error':'payment required'
                }, 402)  # 402 Payment Required

            # Calculate the period as the current year and month
            period = f'{end_time.year}-{end_time.month}'

            log = {
                'enterprise_id': enterprise_id,
                'endpoint': request.endpoint,
                'method': request.method,
                'duration': duration,
                'period': period,
                'timestamp': datetime.datetime.now(),
            }
            db['request_logs'].insert_one(log)

        return response
    
    return app
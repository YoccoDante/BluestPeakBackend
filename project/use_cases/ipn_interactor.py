from env import IPN_SECRET_WORD
import hashlib
from project.interface_adapters.dao.enterpriseDao import EnterpriseDao

class VerifyIpnInteractor:
    def __init__(self, enterprise_dao:EnterpriseDao):
        self.enterprise_dao = enterprise_dao

    def execute(self, ipn_message, enterprise_id):
        secret_word = IPN_SECRET_WORD
        string_to_hash = ipn_message['sale_id'] + ipn_message['vendor_id'] + ipn_message['invoice_id'] + secret_word
        md5_hash = hashlib.md5(string_to_hash.encode('utf-8')).hexdigest().upper()
        if md5_hash != ipn_message['HASH']:
            raise ValueError('Invalid IPN message hash')
        if ipn_message['enterprise_id'] != enterprise_id:
            raise ValueError('Mismatched enterprise ID in IPN message')
        if ipn_message['message_type'] != 'ORDER_CREATED':
            raise ValueError('Payment not committed')
        # If the IPN message is verified and the payment was successful, mark the enterprise as paid
        self.enterprise_dao.mark_as_paid(enterprise_id)
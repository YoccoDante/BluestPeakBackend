from botocore.exceptions import ClientError
from project.frameworks_and_drivers.aws_clients import SESClient

class SendEmailInteractor:
    def __init__(self):
        self.ses_client = SESClient.get_instance().client

    def send_email(self, to_address, from_address, subject, body_text, body_html):
        try:
            response = self.ses_client.send_email(
                Destination={
                    'ToAddresses': [to_address],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': 'UTF-8',
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': 'UTF-8',
                            'Data': body_text,
                        },
                    },
                    'Subject': {
                        'Charset': 'UTF-8',
                        'Data': subject,
                    },
                },
                Source=from_address,
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            raise e
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])
            raise response['MessageId']
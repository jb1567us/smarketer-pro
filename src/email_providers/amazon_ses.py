import os
import boto3
from botocore.exceptions import ClientError
from config import config
from .base import EmailProvider

class AmazonSESProvider(EmailProvider):
    def __init__(self):
        self.aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.region_name = os.getenv("AWS_REGION", "us-east-1")
        self.from_email = config['email'].get('from_email')
        
    def send_html_email(self, to_email, subject, html_content):
        if not self.aws_access_key or not self.aws_secret_key:
            print("  [SES] Error: AWS credentials not found.")
            return {
                "success": False,
                "provider": "amazon_ses",
                "message_id": None,
                "metadata": {"error": "Credentials Missing"}
            }

        try:
            client = boto3.client(
                'ses',
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
            
            response = client.send_email(
                Source=self.from_email,
                Destination={
                    'ToAddresses': [to_email],
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': html_content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            
            msg_id = response['MessageId']
            print(f"  [SES] Email sent to {to_email} (ID: {msg_id})")
            return {
                "success": True,
                "provider": "amazon_ses",
                "message_id": msg_id,
                "metadata": {"status": "success"}
            }
            
        except ClientError as e:
            print(f"  [SES] Failed to send to {to_email}: {e.response['Error']['Message']}")
            return {
                "success": False,
                "provider": "amazon_ses",
                "message_id": None,
                "metadata": {"error": e.response['Error']['Message']}
            }
        except Exception as e:
            print(f"  [SES] Unexpected error: {e}")
            return {
                "success": False,
                "provider": "amazon_ses",
                "message_id": None,
                "metadata": {"error": str(e)}
            }

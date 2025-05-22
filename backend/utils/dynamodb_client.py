import os
import boto3
from botocore.exceptions import ClientError

class DynamoDBClient:
    def __init__(self):
        self.table_name = os.environ.get('DYNAMODB_TABLE', 'MonitoringAlerts')
        
        if os.environ.get('LOCALSTACK_HOSTNAME'):
            endpoint_url = f"http://{os.environ.get('LOCALSTACK_HOSTNAME')}:4566"
            self.dynamodb = boto3.resource(
                'dynamodb',
                endpoint_url=endpoint_url,
                region_name='us-east-1',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
        else:
            if os.environ.get('AWS_SAM_LOCAL') or os.environ.get('RUNNING_LOCALLY'):
                endpoint_url = "http://localhost:4566"
                self.dynamodb = boto3.resource(
                    'dynamodb',
                    endpoint_url=endpoint_url,
                    region_name='us-east-1',
                    aws_access_key_id='test',
                    aws_secret_access_key='test'
                )
            else:
                self.dynamodb = boto3.resource('dynamodb')
    
    def save_item(self, item):
        try:
            table = self.dynamodb.Table(self.table_name)
            response = table.put_item(Item=item)
            return response
        except ClientError as e:
            print(f"Erro ao salvar item no DynamoDB: {str(e)}")
            raise e
    
    def get_item(self, id):
        try:
            table = self.dynamodb.Table(self.table_name)
            response = table.get_item(Key={'id': id})
            return response.get('Item')
        except ClientError as e:
            print(f"Erro ao recuperar item do DynamoDB: {str(e)}")
            return None
    
    def scan_items(self, limit=100):
        try:
            table = self.dynamodb.Table(self.table_name)
            response = table.scan(Limit=limit)
            return response.get('Items', [])
        except ClientError as e:
            print(f"Erro ao listar itens do DynamoDB: {str(e)}")
            return [] 
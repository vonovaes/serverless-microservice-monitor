import os
import boto3
from botocore.exceptions import ClientError

class SNSPublisher:
    """
    Cliente para publicação de mensagens no SNS (local ou na AWS)
    """
    
    def __init__(self):
        """
        Inicializa o cliente do SNS
        
        Se a variável de ambiente LOCALSTACK_HOSTNAME estiver definida,
        configura para usar o LocalStack, caso contrário usa o serviço AWS real
        """
        self.topic_arn = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:000000000000:monitoring-alerts')
        
        if os.environ.get('LOCALSTACK_HOSTNAME'):
            endpoint_url = f"http://{os.environ.get('LOCALSTACK_HOSTNAME')}:4566"
            self.sns = boto3.client(
                'sns',
                endpoint_url=endpoint_url,
                region_name='us-east-1',
                aws_access_key_id='test',
                aws_secret_access_key='test'
            )
        else:
            if os.environ.get('AWS_SAM_LOCAL') or os.environ.get('RUNNING_LOCALLY'):
                endpoint_url = "http://localhost:4566"
                self.sns = boto3.client(
                    'sns',
                    endpoint_url=endpoint_url,
                    region_name='us-east-1',
                    aws_access_key_id='test',
                    aws_secret_access_key='test'
                )
            else:
                self.sns = boto3.client('sns')
    
    def publish_message(self, subject, message):
        """
        Publica uma mensagem no tópico do SNS
        
        Args:
            subject (str): Assunto da mensagem
            message (str): Corpo da mensagem (geralmente um JSON serializado)
            
        Returns:
            dict: Resposta do SNS
        """
        try:
            response = self.sns.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            print(f"Mensagem publicada no SNS com MessageId: {response['MessageId']}")
            return response
        except ClientError as e:
            print(f"Erro ao publicar mensagem no SNS: {str(e)}")
            raise e 
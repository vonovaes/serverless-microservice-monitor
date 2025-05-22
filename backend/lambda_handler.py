import json
import os
import uuid
from datetime import datetime

from utils.dynamodb_client import DynamoDBClient
from utils.sns_publisher import SNSPublisher
from utils.sqs_parser import SQSParser

def lambda_handler(event, context):
    try:
        dynamodb = DynamoDBClient()
        sns = SNSPublisher()
        sqs_parser = SQSParser()
        
        processed_messages = []
        for record in event.get('Records', []):
            message_data = sqs_parser.parse_message(record)
            
            message_data['id'] = str(uuid.uuid4())
            message_data['timestamp'] = datetime.utcnow().isoformat()
            message_data['status'] = 'PROCESSED'
            
            dynamodb.save_item(message_data)
            
            alert_message = {
                'id': message_data['id'],
                'tipo': message_data.get('tipo', 'DESCONHECIDO'),
                'serviço': message_data.get('servico', 'DESCONHECIDO'),
                'timestamp': message_data['timestamp'],
                'mensagem': f"Alerta processado: {message_data.get('mensagem', 'Sem detalhes')}"
            }
            
            sns.publish_message(
                subject=f"Alerta de monitoramento - {message_data.get('tipo', 'DESCONHECIDO')}",
                message=json.dumps(alert_message)
            )
            
            processed_messages.append(message_data['id'])
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Processadas {len(processed_messages)} mensagens com sucesso',
                'processed_ids': processed_messages
            })
        }
        
    except Exception as e:
        print(f"Erro ao processar mensagens: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Erro ao processar mensagens: {str(e)}'
            })
        }

if __name__ == "__main__":
    sample_event = {
        "Records": [
            {
                "messageId": "19dd0b57-b21e-4ac1-bd88-01bbb068cb78",
                "receiptHandle": "MessageReceiptHandle",
                "body": json.dumps({
                    "tipo": "CPU_HIGH",
                    "servico": "api-gateway",
                    "valor": 92.5,
                    "limite": 80.0,
                    "mensagem": "Uso de CPU acima do limite"
                }),
                "attributes": {
                    "ApproximateReceiveCount": "1",
                    "SentTimestamp": "1523232000000",
                    "SenderId": "123456789012",
                    "ApproximateFirstReceiveTimestamp": "1523232000001"
                },
                "messageAttributes": {},
                "md5OfBody": "7b270e59b47ff90a553787216d55d91d",
                "eventSource": "aws:sqs",
                "eventSourceARN": "arn:aws:sqs:us-east-1:123456789012:MonitoringQueue",
                "awsRegion": "us-east-1"
            }
        ]
    }
    
    result = lambda_handler(sample_event, None)
    print(result) 
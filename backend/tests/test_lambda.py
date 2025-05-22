import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Adiciona o diretório pai ao path para importar os módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lambda_handler import lambda_handler
from utils.dynamodb_client import DynamoDBClient
from utils.sns_publisher import SNSPublisher
from utils.sqs_parser import SQSParser

class TestLambdaHandler(unittest.TestCase):
    """
    Testes para a função Lambda Handler
    """
    
    def setUp(self):
        """
        Configura o ambiente para os testes
        """
        # Configura variáveis de ambiente para testes
        os.environ['RUNNING_LOCALLY'] = 'true'
        os.environ['DYNAMODB_TABLE'] = 'MonitoringAlerts'
        os.environ['SNS_TOPIC_ARN'] = 'arn:aws:sns:us-east-1:000000000000:monitoring-alerts'
        
        # Evento SQS de exemplo para testes
        self.sample_event = {
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
        
        # Mock para DynamoDB
        self.dynamodb_mock = MagicMock()
        self.dynamodb_mock.save_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        # Mock para SNS
        self.sns_mock = MagicMock()
        self.sns_mock.publish_message.return_value = {'MessageId': 'test-message-id'}
        
        # Mock para SQS Parser
        self.sqs_parser_mock = MagicMock()
        self.sqs_parser_mock.parse_message.return_value = {
            "tipo": "CPU_HIGH",
            "servico": "api-gateway",
            "valor": 92.5,
            "limite": 80.0,
            "mensagem": "Uso de CPU acima do limite",
            "is_valid": True
        }
    
    @patch('lambda_handler.DynamoDBClient')
    @patch('lambda_handler.SNSPublisher')
    @patch('lambda_handler.SQSParser')
    def test_lambda_handler_success(self, mock_sqs_parser, mock_sns_publisher, mock_dynamodb_client):
        """
        Testa o funcionamento correto do Lambda Handler
        """
        # Configura os mocks
        mock_dynamodb_client.return_value = self.dynamodb_mock
        mock_sns_publisher.return_value = self.sns_mock
        mock_sqs_parser.return_value = self.sqs_parser_mock
        
        response = lambda_handler(self.sample_event, {})
        
        # Verifica o resultado
        self.assertEqual(response['statusCode'], 200)
        
        # Verifica se os métodos foram chamados corretamente
        self.sqs_parser_mock.parse_message.assert_called_once()
        self.dynamodb_mock.save_item.assert_called_once()
        self.sns_mock.publish_message.assert_called_once()
        
        # Verifica o conteúdo da resposta
        body = json.loads(response['body'])
        self.assertIn('message', body)
        self.assertIn('processed_ids', body)
        self.assertEqual(len(body['processed_ids']), 1)
    
    @patch('lambda_handler.DynamoDBClient')
    @patch('lambda_handler.SNSPublisher')
    @patch('lambda_handler.SQSParser')
    def test_lambda_handler_no_records(self, mock_sqs_parser, mock_sns_publisher, mock_dynamodb_client):
        """
        Testa o comportamento quando não há registros na mensagem
        """
        # Configura os mocks
        mock_dynamodb_client.return_value = self.dynamodb_mock
        mock_sns_publisher.return_value = self.sns_mock
        mock_sqs_parser.return_value = self.sqs_parser_mock
        
        # Evento sem registros
        empty_event = {"Records": []}
        
        # Executa a função Lambda
        response = lambda_handler(empty_event, {})
        
        # Verifica o resultado
        self.assertEqual(response['statusCode'], 200)
        
        # Verifica que nenhum método foi chamado
        self.sqs_parser_mock.parse_message.assert_not_called()
        self.dynamodb_mock.save_item.assert_not_called()
        self.sns_mock.publish_message.assert_not_called()
        
        # Verifica o conteúdo da resposta
        body = json.loads(response['body'])
        self.assertIn('message', body)
        self.assertIn('processed_ids', body)
        self.assertEqual(len(body['processed_ids']), 0)
    
    @patch('lambda_handler.DynamoDBClient')
    @patch('lambda_handler.SNSPublisher')
    @patch('lambda_handler.SQSParser')
    def test_lambda_handler_exception(self, mock_sqs_parser, mock_sns_publisher, mock_dynamodb_client):
        """
        Testa o tratamento de exceções no Lambda Handler
        """
        # Configura os mocks para lançar uma exceção
        mock_dynamodb_client.return_value = self.dynamodb_mock
        mock_sns_publisher.return_value = self.sns_mock
        mock_sqs_parser.return_value = self.sqs_parser_mock
        self.sqs_parser_mock.parse_message.side_effect = Exception("Erro de teste")
        
        # Executa a função Lambda
        response = lambda_handler(self.sample_event, {})
        
        # Verifica o resultado
        self.assertEqual(response['statusCode'], 500)
        
        # Verifica o conteúdo da resposta
        body = json.loads(response['body'])
        self.assertIn('message', body)
        self.assertIn('Erro ao processar mensagens', body['message'])

if __name__ == '__main__':
    unittest.main() 
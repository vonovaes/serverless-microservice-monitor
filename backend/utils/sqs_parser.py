import json

class SQSParser:
    def parse_message(self, record):
        try:
            message_body = record.get('body', '{}')
            
            if isinstance(message_body, str):
                message_data = json.loads(message_body)
            else:
                message_data = message_body
                
            if not self._validate_message(message_data):
                print(f"Mensagem inválida recebida: {message_body}")
                message_data['is_valid'] = False
                return message_data
            
            message_data['is_valid'] = True
            
            return message_data
            
        except json.JSONDecodeError as e:
            print(f"Erro ao fazer parse do JSON da mensagem SQS: {str(e)}")
            return {'is_valid': False, 'error': 'JSON inválido', 'raw_message': record.get('body', '{}')}
        
        except Exception as e:
            print(f"Erro ao processar mensagem SQS: {str(e)}")
            return {'is_valid': False, 'error': str(e), 'raw_message': record.get('body', '{}')}
    
    def _validate_message(self, message_data):
        required_fields = ['tipo', 'servico']
        
        for field in required_fields:
            if field not in message_data:
                return False
                
        return True 
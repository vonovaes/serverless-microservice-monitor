# Sistema de Monitoramento Serverless

Este projeto simula um sistema de monitoramento baseado em microsserviços com arquitetura serverless utilizando AWS (simulada localmente com LocalStack).

## Visão Geral

O sistema realiza as seguintes operações:

1. Recebe mensagens de monitoramento via AWS SQS
2. Processa os dados usando uma função AWS Lambda em Python
3. Persiste informações em uma tabela do DynamoDB
4. Envia um alerta para um tópico AWS SNS após o processamento

## Tecnologias Utilizadas

- Python 3.9+
- AWS Lambda (simulada localmente)
- Amazon SQS (via LocalStack)
- Amazon SNS (via LocalStack)
- Amazon DynamoDB (via LocalStack)
- Docker e Docker Compose
- pytest para testes unitários

## Estrutura do Projeto

```
serverless-event-driven-processor/
├── backend/                   # Código da função Lambda
│   ├── lambda_handler.py      # Handler principal
│   ├── requirements.txt       # Dependências Python
│   ├── utils/                 # Utilitários
│   │   ├── dynamodb_client.py # Cliente DynamoDB
│   │   ├── sns_publisher.py   # Cliente SNS
│   │   └── sqs_parser.py      # Parser para mensagens SQS
│   └── tests/                 # Testes unitários
│       └── test_lambda.py     # Testes para o handler
├── infra/                     # Infraestrutura
│   ├── docker-compose.yml     # Configuração do LocalStack
│   ├── setup_localstack.sh    # Script para criar recursos 
│   └── terraform/             # (Opcional) IaC com Terraform
└── README.md                  # Este arquivo
```

## Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.9 ou superior
- Pip (gerenciador de pacotes Python)

### Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/seu-usuario/serverless-event-driven-processor.git
   cd serverless-event-driven-processor
   ```

2. Instale as dependências Python:
   ```
   cd backend
   pip install -r requirements.txt
   ```

3. Inicie o LocalStack com os serviços AWS:
   ```
   cd ../infra
   docker-compose up -d
   ```

### Executando a Aplicação

1. Para executar a função Lambda localmente:
   ```
   cd ../backend
   python lambda_handler.py
   ```

2. Para enviar uma mensagem de teste para a fila SQS:
   ```
   AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=http://localhost:4566 sqs send-message \
     --queue-url=http://localhost:4566/000000000000/MonitoringQueue \
     --message-body='{"tipo":"CPU_HIGH","servico":"api-gateway","valor":95.8,"limite":80.0,"mensagem":"Uso de CPU crítico"}'
   ```

3. Para verificar os dados salvos no DynamoDB:
   ```
   AWS_ACCESS_KEY_ID=test AWS_SECRET_ACCESS_KEY=test aws --endpoint-url=http://localhost:4566 dynamodb scan \
     --table-name MonitoringAlerts
   ```

### Executando os Testes

Para executar os testes unitários:
```
cd backend
pytest -v
```

## Formato das Mensagens

As mensagens devem seguir o formato:

```json
{
  "tipo": "CPU_HIGH",           
  "servico": "api-gateway",     
  "valor": 92.5,                
  "limite": 80.0,               
  "mensagem": "Uso de CPU acima do limite"  
}
```

## Variáveis de Ambiente

- `DYNAMODB_TABLE`: Nome da tabela DynamoDB (padrão: "MonitoringAlerts")
- `SNS_TOPIC_ARN`: ARN do tópico SNS (padrão: "arn:aws:sns:us-east-1:000000000000:monitoring-alerts")
- `LOCALSTACK_HOSTNAME`: Hostname do LocalStack (para desenvolvimento local)
- `RUNNING_LOCALLY`: Flag para indicar execução local

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
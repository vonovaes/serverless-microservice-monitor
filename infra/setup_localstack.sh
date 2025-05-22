#!/bin/bash

# Endpoint do LocalStack
endpoint="http://localstack:4566"

echo "Configurando recursos no LocalStack..."

# Cria a fila SQS
echo "Criando fila SQS: MonitoringQueue..."
aws --endpoint-url=$endpoint sqs create-queue \
  --queue-name MonitoringQueue \
  --attributes '{
    "VisibilityTimeout": "30",
    "MessageRetentionPeriod": "86400"
  }'

# Cria o tópico SNS
echo "Criando tópico SNS: monitoring-alerts..."
aws --endpoint-url=$endpoint sns create-topic \
  --name monitoring-alerts

# Cria a tabela DynamoDB
echo "Criando tabela DynamoDB: MonitoringAlerts..."
aws --endpoint-url=$endpoint dynamodb create-table \
  --table-name MonitoringAlerts \
  --attribute-definitions \
      AttributeName=id,AttributeType=S \
  --key-schema \
      AttributeName=id,KeyType=HASH \
  --provisioned-throughput \
      ReadCapacityUnits=5,WriteCapacityUnits=5

# Lista os recursos criados para verificação
echo "Recursos criados:"
echo "SQS Queues:"
aws --endpoint-url=$endpoint sqs list-queues
echo "SNS Topics:"
aws --endpoint-url=$endpoint sns list-topics
echo "DynamoDB Tables:"
aws --endpoint-url=$endpoint dynamodb list-tables

echo "Configuração concluída!" 
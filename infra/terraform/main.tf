provider "aws" {
  region = "us-east-1"
}

# Fila SQS
resource "aws_sqs_queue" "monitoring_queue" {
  name                       = "MonitoringQueue"
  visibility_timeout_seconds = 30
  message_retention_seconds  = 86400
  
  tags = {
    Environment = var.environment
    Project     = "MonitoringSystem"
  }
}

# Tópico SNS
resource "aws_sns_topic" "monitoring_alerts" {
  name = "monitoring-alerts"
  
  tags = {
    Environment = var.environment
    Project     = "MonitoringSystem"
  }
}

# Tabela DynamoDB
resource "aws_dynamodb_table" "monitoring_alerts" {
  name           = "MonitoringAlerts"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  tags = {
    Environment = var.environment
    Project     = "MonitoringSystem"
  }
}

# IAM Role para a função Lambda
resource "aws_iam_role" "lambda_role" {
  name = "monitoring_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

# Política de permissões para a função Lambda
resource "aws_iam_role_policy" "lambda_policy" {
  name = "monitoring_lambda_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action = [
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Effect   = "Allow"
        Resource = aws_sqs_queue.monitoring_queue.arn
      },
      {
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:Scan"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.monitoring_alerts.arn
      },
      {
        Action = [
          "sns:Publish"
        ]
        Effect   = "Allow"
        Resource = aws_sns_topic.monitoring_alerts.arn
      }
    ]
  })
}

# Função Lambda
resource "aws_lambda_function" "monitoring_lambda" {
  filename      = var.lambda_zip_path
  function_name = "monitoring-processor"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_handler.lambda_handler"
  runtime       = "python3.9"
  timeout       = 30
  memory_size   = 128

  environment {
    variables = {
      DYNAMODB_TABLE = aws_dynamodb_table.monitoring_alerts.name
      SNS_TOPIC_ARN  = aws_sns_topic.monitoring_alerts.arn
    }
  }

  tags = {
    Environment = var.environment
    Project     = "MonitoringSystem"
  }
}

# Mapeamento de origem de eventos para conectar SQS e Lambda
resource "aws_lambda_event_source_mapping" "sqs_lambda_mapping" {
  event_source_arn = aws_sqs_queue.monitoring_queue.arn
  function_name    = aws_lambda_function.monitoring_lambda.function_name
  batch_size       = 10
} 
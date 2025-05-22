variable "environment" {
  description = "Ambiente de implantação (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "lambda_zip_path" {
  description = "Caminho para o arquivo ZIP da função Lambda"
  type        = string
  default     = "../../lambda.zip"
}

variable "aws_region" {
  description = "Região AWS para implantação dos recursos"
  type        = string
  default     = "us-east-1"
} 
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "assets" {
  bucket = var.assets_bucket
}

resource "aws_ecs_cluster" "main" {
  name = "insightpro"
}

resource "aws_cloudwatch_log_group" "api" {
  name              = "/ecs/insightpro-api"
  retention_in_days = 30
}

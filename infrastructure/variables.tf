variable "aws_region" {
  description = "AWS region to create resources"
  default     = "eu-central-1"
}

variable "project_id" {
  description = "project_id"
  default = "parkinson-disease-prediction"
}

variable "model_bucket" {
  description = "s3_bucket"
}

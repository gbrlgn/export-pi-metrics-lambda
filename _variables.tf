variable "enabled" {
  default = true
}

variable "env" {
  default = "dev"
}

variable "output_name" {
  description = "Name to function's deployment package into local filesystem"
  default = "lambda_dir.zip"
}
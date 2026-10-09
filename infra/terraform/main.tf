terraform{
    required_providers {
        aws = {
            source  = "hashicorp/aws"
         version = "~> 6.0"
        }
    }
}
provider "aws" {
     region = "ap-south-1"
   }

data "aws_vpc" "default" {
  default = true
}

output "default_vpc_id" {
  value = data.aws_vpc.default.id
}

variable "my_ip" {
     type = string
}
resource "aws_security_group" "app" {
  name        = "workforce-tf-sg"
  description = "Workforce app (Terraform)"
  vpc_id      = data.aws_vpc.default.id
  ingress {
    description = "SSH from my IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }
  ingress {
    description = "Streamlit from my IP"
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
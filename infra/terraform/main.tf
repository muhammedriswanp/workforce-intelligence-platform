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
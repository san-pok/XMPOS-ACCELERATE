variable "aws_region" {
    default     = "ap-southeast-2" #  region
  description = "AWS region to launch the EC2 instance"
}

variable "ami_id" {
    default     = "ami-04f5097681773b989" #   AMI ID
  description = "AMI ID of the EC2 instance"
}

variable "instance_type" {
    default     = "t2.micro" #  instance type
  description = "Instance type of the EC2 instance"
}

output "public_ip" {
  value       = aws_instance.EC2-create-from-button.public_ip
  description = "Public IP Address of EC2 instance"
}

output "instance_id" {
  value       = aws_instance.EC2-create-from-button.id
  description = "Instance ID"
}

# output "private_ip" {
#   value = aws_instance.EC2-create-from-button.private_ip
# }

output "instance_state" {
  value = aws_instance.EC2-create-from-button.instance_state
}

output "instance_type" {
  value = aws_instance.EC2-create-from-button.instance_type
}

output "availability_zone" {
  value = aws_instance.EC2-create-from-button.availability_zone
}

output "ami_id" {
  value = aws_instance.EC2-create-from-button.ami
}

output "key_name" {
  value = aws_instance.EC2-create-from-button.key_name
}

# output "aami_id" {
#   value = aws_instance.EC2-create-from-button.ami
#   description = "Fake output, to take real ami_id in the Parsed body in utils.js"
# }

# output "instance_region" {
#   value = aws_instance.EC2-create-from-button.region
# }

output "instance_region" {
  value = data.aws_region.current.name
}
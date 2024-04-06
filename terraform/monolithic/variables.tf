variable "aws_region" {
    # default     = "ap-southeast-2" #  region
  description = "AWS region to launch the EC2 instance"
}

variable "ami_id" {
    # default     = "ami-04f5097681773b989" #   AMI ID
  description = "AMI ID of the EC2 instance"
}

variable "instance_type" {
    # default     = "t2.micro" #  instance type
  description = "Instance type of the EC2 instance"
}

variable "key_name" {
  description = "The name of the SSH key to use for the instance"
  type        = string
  default     = "wordpress_server"  # Default value
}

variable "security_group_name" {
  description = "Security group name to use for the instance"
  type        = string
  default     = "wordpress_server"  # Default value
}

variable "security_group_description" {
  description = "Security group description to use for the instance"
  type        = string
  default     = "wordpress_server"  # Default value
}

variable "create_security_group" {
  type    = bool
  default = true  # You can set a default value if needed
}

variable "allow_ssh" {
  description = "This variable is for SSH allow or not allow"
  type = bool
  default = true
}

variable "allow_http" {
  description = "This variable is for HTTP allow or not allow to the instance"
  type = bool
  default = true
}
variable "storage_size_gb" {
  description = "This variable is for ebs_storage"
  type = number
  default = 8
}

variable "database_type" {
  description = "Type of database to install. Choose from 'mysql', 'mariadb', or 'postgresql'."
  type        = string
  default     = "mysql"
}

variable "web_server" {
  description = "Type of Web Server Engine. Apache2 or Nginx"
  type    = string
  default = "apache2"
}


output "public_ip" {
  value       = aws_instance.EC2-create-from-button.public_ip
  description = "Public IP Address of EC2 instance"
}

output "instance_id" {
  value       = aws_instance.EC2-create-from-button.id
  description = "Instance ID"
}

output "private_ip" {
  value = aws_instance.EC2-create-from-button.private_ip
}

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

output "database_type_selected" {
  value = var.database_type
  description = "The selected database type"
}
output "instance_tags" {
  value = aws_instance.EC2-create-from-button.tags
}

output "instance_region" {
  value = data.aws_region.current.name
  
}

output "public_dns" {
  value = aws_instance.EC2-create-from-button.public_dns
}


output "existing_security_group_ids" {
  value = data.aws_security_groups.existing_sg.ids
}

output "create_security_group" {
  value = length(aws_security_group.sg_name) > 0  # Outputs true if the security group is created
}


output "mysql_content_executed" {
  value = local.mysql_content_available > 0 ? "MySQL Apache2 server content executed" : "MySQL Apache2 server content not executed"
}

output "mariadb_content_executed" {
  value = local.mariadb_content_available > 0 ? "MariaDB Apache2 server content executed" : "MariaDB Apache 2 server content not executed"
}

output "mariadb_nginx_content_executed" {
  value = local.mariadb_nginx_content_available > 0 ? "MariaDB Nginx content server executed" : "MariaDB Nginx server content not executed"
}


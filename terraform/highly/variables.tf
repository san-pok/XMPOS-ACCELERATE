variable "aws_region" {
  default = "ap-southeast-2"
  description = "The AWS region where the resources will be provisioned."
}
#Singapore ap-southeast-1 ,Australia ap-southeast-2 ,North California us-west-1

variable "namespace" {
  default = "xmop"
  description = "Namespace for project"
}

variable "ami_id" {
  description = "The ID of the AMI to use for the EC2 instance."
}

variable "instance_type" {
  description = "The type of EC2 instance to launch."
}

variable "min_instances" {
  description = "The minimum number of  EC2 instance to launch."
}

variable "max_instances" {
  description = "The maximum number of  EC2 instance to launch."
}

variable "desired_instances" {
  description = "The desired number of  EC2 instance to launch."
}

variable "key_pair_name" {
  description = "The name of the key pair to associate with the EC2 instance."
}

variable "storage_size" {
  description = "The size of the root volume for the EC2 instance (in GiB)."
  default     = 8
}

variable "storage_type" {
  description = "The type of storage for the root volume (e.g., gp2, gp3)."
  default     = "gp3"
}
#GP3 volumes offer higher performance, more flexibility in provisioning throughput, and potentially lower costs compared to GP2 volumes.

variable "db_engine" {
  description = "The engine type for RDS (MYSQL or PostgreSQL) ."
  default     = "mysql"
}

variable "engine_version" {
  description = "The version of the database engine"
  default     = "8.0"
}

variable "instance_class" {
  description = "The instance type for the RDS instance"
  default     = "db.t3.micro"
}

variable "rds_storage" {
  description = "The storage size for the RDS instance"
  default     = "20"
}

variable "environment" {
  description = "The environment for RDS"
  default     = "Development"
  #Production or Development
}
variable "enable_multi_az" {
  description = "Enable or disable Multiple Availability zone of RDS"
  default     = "true"

}

variable "db_username" {
  default     = "admin"
}

variable "db_password" {
  default     = "password"
}
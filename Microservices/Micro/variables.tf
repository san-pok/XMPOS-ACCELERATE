variable "aws_region" {
  default = "ap-southeast-2"
  description = "The AWS region where the resources will be provisioned."
}

variable "vpc_name" {
  default = "MainVPC"
  description = "The name of the Virtual Private Cloud (VPC)."
}

variable "vpc_cidr_block" {
  default = "10.0.0.0/16"
  description = "The CIDR block for the VPC."
}

variable "internet_gateway_name" {
  default = "MainInternetGateway"
  description = "The name of the Internet Gateway."
}

variable "public_subnet_cidr_block_az1" {
  default = "10.0.1.0/24"
  description = "The CIDR block for the public subnet in Availability Zone 1."
}

variable "availability_zone" {
  default = "ap-southeast-2a"
  description = "The Availability Zone for the resources."
}

variable "public_subnet_name_az1" {
  default = "PublicSubnetAZ1"
  description = "The name of the public subnet in Availability Zone 1."
}

variable "public_route_table_name" {
  default = "PublicRouteTable"
  description = "The name of the public route table."
}

variable "security_group_name" {
  default = "example-service-sg"
  description = "The name of the security group for the ECS service."
}

variable "security_group_description" {
  default = "Security group for the ECS service"
  description = "The description of the security group."
}

variable "iam_role_name" {
  default = "ecs-task-execution-role"
  description = "The name of the IAM role for ECS task execution."
}

variable "ecs_cluster_name" {
  default = "example-cluster"
  description = "The name of the ECS cluster."
}

variable "ecs_task_family" {
  default = "example-task"
  description = "The family name of the ECS task definition."
}

variable "ecs_task_cpu" {
  default = 256
  description = "The CPU units for the ECS task."
}

variable "ecs_task_memory" {
  default = 512
  description = "The memory for the ECS task (in MiB)."
}


variable "ecs_service_name" {
  default = "example-service"
  description = "The name of the ECS service."
}

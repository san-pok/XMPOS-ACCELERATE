variable "aws_region" {
  default = "ap-southeast-2"
  description = "The AWS region where the resources will be provisioned."
}
#Singapore ap-southeast-1 ,Australia ap-southeast-2 ,North California us-west-1

variable "vpc_name" {
  default = "HighVPC"
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

variable "instance_name" {
  description = "The name of the EC2 instance."
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
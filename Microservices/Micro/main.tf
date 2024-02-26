#// Define VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr_block
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = var.vpc_name
  }
}
#
#// Define Internet Gateway
#resource "aws_internet_gateway" "gw" {
#  vpc_id = aws_vpc.main.id
#  tags = {
#    Name = var.internet_gateway_name
#  }
#}
#
#// Define Public Subnet in Availability Zone 1
#resource "aws_subnet" "public_subnet_az1" {
#  vpc_id                  = aws_vpc.main.id
#  cidr_block              = var.public_subnet_cidr_block_az1
#  availability_zone       = var.availability_zone
#  map_public_ip_on_launch = true
#  tags = {
#    Name = var.public_subnet_name_az1
#  }
#}
#
#// Define Public Route Table
#resource "aws_route_table" "public" {
#  vpc_id = aws_vpc.main.id
#
#  route {
#    cidr_block = "0.0.0.0/0"
#    gateway_id = aws_internet_gateway.gw.id
#  }
#
#  tags = {
#    Name = var.public_route_table_name
#  }
#}
#
#// Associate Public Route Table with Public Subnets
#resource "aws_route_table_association" "public_association_az1" {
#  subnet_id      = aws_subnet.public_subnet_az1.id
#  route_table_id = aws_route_table.public.id
#}
#
#// Define the security group for the ECS service
#resource "aws_security_group" "example_service_sg" {
#  name        = var.security_group_name
#  description = var.security_group_description
#  vpc_id      = aws_vpc.main.id
#
#  ingress {
#    from_port   = 80
#    to_port     = 80
#    protocol    = "tcp"
#    cidr_blocks = [
#      "0.0.0.0/0"  // IPv4
#    ]
#  }
#
#  ingress {
#    from_port   = 80
#    to_port     = 80
#    protocol    = "tcp"
#    ipv6_cidr_blocks = [
#      "::/0"      // IPv6
#    ]
#  }
#
#  egress {
#    from_port   = 0
#    to_port     = 0
#    protocol    = "-1"
#    cidr_blocks = ["0.0.0.0/0"] // Allowing all outbound traffic
#  }
#}

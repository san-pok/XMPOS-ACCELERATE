resource "aws_vpc" "xmop_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = {
    Name = "${var.namespace}-hVPC"
  }
}

resource "aws_internet_gateway" "xmop_internet_gateway" {
  vpc_id = aws_vpc.xmop_vpc.id

  tags = {
    Name = "${var.namespace}-hInternetGateway"
  }
}

//Public Subnets
resource "aws_subnet" "xmop_subnet_1" {
  vpc_id            = aws_vpc.xmop_vpc.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = true
}

resource "aws_subnet" "xmop_subnet_2" {
  vpc_id            = aws_vpc.xmop_vpc.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "${var.aws_region}b"
  map_public_ip_on_launch = true
}

//private subnet
resource "aws_subnet" "xmop_subnet_3" {
  vpc_id            = aws_vpc.xmop_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.aws_region}a"
  map_public_ip_on_launch = false
}

resource "aws_subnet" "xmop_subnet_4" {
  vpc_id            = aws_vpc.xmop_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "${var.aws_region}b"
  map_public_ip_on_launch = false
}

resource "aws_route_table" "xmop_route_table" {
  vpc_id = aws_vpc.xmop_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.xmop_internet_gateway.id
  }
}

resource "aws_route_table_association" "xmop_route_association_1" {
  subnet_id      = aws_subnet.xmop_subnet_1.id
  route_table_id = aws_route_table.xmop_route_table.id
}

resource "aws_route_table_association" "xmop_route_association_2" {
  subnet_id      = aws_subnet.xmop_subnet_2.id
  route_table_id = aws_route_table.xmop_route_table.id
}

resource "aws_route_table_association" "xmop_route_association_3" {
  subnet_id      = aws_subnet.xmop_subnet_3.id
  route_table_id = aws_route_table.xmop_route_table.id
}

resource "aws_route_table_association" "xmop_route_association_4" {
  subnet_id      = aws_subnet.xmop_subnet_4.id
  route_table_id = aws_route_table.xmop_route_table.id
}

resource "aws_security_group" "xmop_wordpress_sg" {
  name        = "${var.namespace}-hWordpress_SG"
  description = "Security group for WordPress deployment"
  vpc_id      = aws_vpc.xmop_vpc.id

  ingress {
    from_port   = 80 // HTTP
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443 //HTTPS
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port = 22 //SSH
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


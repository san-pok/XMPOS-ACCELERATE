resource "aws_security_group" "rds_sg" {
  name     = "${var.namespace}-hrds-security-group"
  description = "Security group for RDS instance"
  vpc_id      =aws_vpc.xmop_vpc.id

  ingress {
    from_port   = 3306  # MySQL port
    to_port     = 3306
    protocol    = "tcp"
    # Allow inbound traffic from WP Security Group
    security_groups = [aws_security_group.xmop_wordpress_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    # Allow outbound traffic to any IP
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "rds-security-group"
  }
}

resource "aws_db_instance" "xmop_rds" {
  identifier           = "${var.namespace}hrdsinstance"
  engine               = var.db_engine
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  allocated_storage    = var.rds_storage
  db_name              = "${var.namespace}hrdsinstance"
  username             = var.db_username
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.xmop_db_subnet_group.name
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  multi_az = var.enable_multi_az

  tags = {
    Environment = var.environment
  }
}


resource "aws_db_subnet_group" "xmop_db_subnet_group" {
  name       = "xmop-db-subnet-group"
  subnet_ids = [aws_subnet.xmop_subnet_3.id, aws_subnet.xmop_subnet_4.id]
}

# Create IAM role for EC2 instances
resource "aws_iam_role" "ec2_role" {
  name               = "ec2-rds-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = {
        Service = "ec2.amazonaws.com"
      },
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2-rds-profile"
  role = aws_iam_role.ec2_role.name
}

resource "aws_iam_role_policy_attachment" "rds_policy_attachment" {
  role       = aws_iam_role.ec2_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonRDSFullAccess"
}

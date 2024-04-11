resource "aws_security_group" "rds_sg" {
  name        = "rds-security-group"
  description = "Security group for RDS instance"
  vpc_id      =aws_vpc.xmop_vpc.id

  ingress {
    from_port   = 3306  # MySQL port
    to_port     = 3306
    protocol    = "tcp"
    security_groups = [aws_security_group.xmop_wordpress_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]  # Allow outbound traffic to any IP (adjust as needed)
  }

  tags = {
    Name = "rds-security-group"
  }
}

resource "aws_db_instance" "example_rds" {
  identifier           = var.identifier
  engine               = var.db_engine
  engine_version       = var.engine_version
  instance_class       = var.instance_class
  allocated_storage    = 20
  db_name              = var.identifier
  username             = var.db_username
  password             = var.db_password
  db_subnet_group_name = aws_db_subnet_group.xmop_db_subnet_group.name
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  tags = {
    Environment = var.environment
  }
}


resource "aws_db_subnet_group" "xmop_db_subnet_group" {
  name       = "xmop-db-subnet-group"
  subnet_ids = [aws_subnet.xmop_subnet_3.id, aws_subnet.xmop_subnet_4.id]  # Use private subnets only
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

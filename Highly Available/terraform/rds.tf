#resource "aws_db_instance" "example_rds" {
#  engine               = "mysql"  # Choose DB Engine Type
#  engine_version       = "5.7"    # Choose Engine Version
#  instance_class       = "db.t2.micro"  # Specify Specs: Instance Type
#  allocated_storage    = 20       # Specify Specs: Storage Capacity (in GB)
#  multi_az             = true    # Choose Availability: Single instance deployment
#
#  db_name                 = "examplerdsinstance1"
#  username             = "admin"
#  password             = "password"
#  db_subnet_group_name = aws_db_subnet_group.example.name
#
#  skip_final_snapshot = true
#
#  tags = {
#    Environment = "Development"  # Define Environment
#  }
#}
#
#resource "aws_db_subnet_group" "example" {
#  name       = "example-db-subnet-group"
#  subnet_ids = [aws_subnet.xmop_subnet_1.id, aws_subnet.xmop_subnet_2.id]
#}

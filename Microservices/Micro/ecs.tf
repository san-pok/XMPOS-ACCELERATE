#// IAM Role for ECS Task Execution
#resource "aws_iam_role" "ecs_task_execution_role" {
#  name               = var.iam_role_name
#  assume_role_policy = jsonencode({
#    Version = "2012-10-17"
#    Statement = [{
#      Effect    = "Allow"
#      Principal = {
#        Service = "ecs-tasks.amazonaws.com"
#      }
#      Action    = "sts:AssumeRole"
#    }]
#  })
#}
#
#resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy_attachment" {
#  role       = aws_iam_role.ecs_task_execution_role.name
#  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
#}
#
#// Define the ECS cluster
#resource "aws_ecs_cluster" "main" {
#  name = var.ecs_cluster_name
#}
#
#// Define the ECS task definition
#resource "aws_ecs_task_definition" "example" {
#  family                   = var.ecs_task_family
#  cpu                      = var.ecs_task_cpu
#  memory                   = var.ecs_task_memory
#  container_definitions    = jsonencode([
#    {
#      name: "wordpress",
#      image: "wordpress:latest",
#      cpu: 0,
#      essential: true,
#      portMappings: [
#        {
#          "containerPort": 80,
#          "hostPort": 80,
#          "protocol": "tcp"
#        }
#      ]
#    }
#  ])
#  network_mode             = "awsvpc"
#  requires_compatibilities = ["FARGATE"]
#  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
#}
#
#// Define the ECS service
#resource "aws_ecs_service" "example_service" {
#  name            = var.ecs_service_name
#  cluster         = aws_ecs_cluster.main.id
#  task_definition = aws_ecs_task_definition.example.arn
#  desired_count   = 1
#
#  launch_type = "FARGATE"
#
#  network_configuration {
#    subnets           = [aws_subnet.public_subnet_az1.id]
#    assign_public_ip  = true
#    security_groups   = [aws_security_group.example_service_sg.id]
#  }
#}

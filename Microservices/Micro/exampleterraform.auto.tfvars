aws_region = "ap-southeast-2"
vpc_name = "ManlyaVPC"
vpc_cidr_block = "10.0.0.0/16"
internet_gateway_name = "MainInternetGateway"
public_subnet_cidr_block_az1 = "10.0.1.0/24"
availability_zone = "ap-southeast-2a"
public_subnet_name_az1 = "PublicSubnetAZ1"
public_route_table_name = "PublicRouteTable"
security_group_name = "example-service-sg"
security_group_description = "Security group for the ECS service"
iam_role_name = "ecs-task-execution-role"
ecs_cluster_name = "example-cluster"
ecs_task_family = "example-task"
ecs_task_cpu = 256
ecs_task_memory = 512
ecs_service_name = "example-service"

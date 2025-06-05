import self
from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_efs as efs,
    aws_logs as logs,
    RemovalPolicy,
    aws_iam as iam,
    Stack,
)
from constructs import Construct

class DbTaskDefStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

         # task role
        task_role = iam.Role.from_role_arn(
            self, "ImportedTaskRole",
            "arn:aws:iam::713767909258:role/ecsTaskExecutionRole-1"
        )

        # Task Definition
        self.task_def = ecs.Ec2TaskDefinition(self, "MyEC2TaskDef",
            family="db",
            network_mode=ecs.NetworkMode.BRIDGE,
            task_role=task_role,
            execution_role=task_role,
            )

        # container
        container = self.task_def.add_container("db-container",
            image=ecs.ContainerImage.from_registry("postgres:latest"),  # минимальный образ
            environment={
                "POSTGRES_DB": "task-db",  # Database name
                "POSTGRES_USER": "taskuser",  # Database user
                "POSTGRES_PASSWORD": "db-user-task",  # Password for PostgreSQL
            },
            memory_limit_mib=256,
            cpu=256
        )

        # port
        container.add_port_mappings(
            ecs.PortMapping(
                container_port=5432,
                host_port=0,
                protocol=ecs.Protocol.TCP,
                name="db-5432",
                app_protocol=ecs.AppProtocol.http,
            )
        )
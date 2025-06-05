import aws_cdk
from aws_cdk import (
    aws_ecs as ecs,
    Stack,
    aws_iam as iam,
)
from constructs import Construct

class BackendTaskDefStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

         # Импорт роли задач (task role)
        task_role = iam.Role.from_role_arn(
            self, "ImportedTaskRole",
            "arn:aws:iam::713767909258:role/ecsTaskExecutionRole-1"
        )

        # Task Definition для EC2 (не Fargate)
        self.task_def = ecs.Ec2TaskDefinition(self, "MyEC2TaskDef",
            family="backend",
            network_mode=ecs.NetworkMode.BRIDGE,
            task_role=task_role,
            execution_role=task_role,
            )

        # Добавляем контейнер
        container = self.task_def.add_container("backend-container",
            image=ecs.ContainerImage.from_registry("713767909258.dkr.ecr.eu-north-1.amazonaws.com/backend:latest"),  # минимальный образ
            memory_limit_mib=256,
            cpu=256
        )

        # Проброс порта
        container.add_port_mappings(
            ecs.PortMapping(
                container_port=8000,
                host_port=0,
                protocol=ecs.Protocol.TCP,
                name="backend-8000",
                app_protocol=ecs.AppProtocol.http,
            )
        )

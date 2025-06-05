from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
)
from constructs import Construct

class DbServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, cluster: ecs.Cluster, task_definition: ecs.Ec2TaskDefinition, target_group, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        service = ecs.Ec2Service(self, "BackendService",
            cluster=cluster,
            task_definition=task_definition,
            desired_count=1,
            service_name="db_service",

        )
        target_group.add_target(service)

from aws_cdk import (
    Stack,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2
)
from constructs import Construct

class BackendServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, cluster: ecs.Cluster, task_definition,target_group,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.service_name = "backend_service"
        service = ecs.Ec2Service(self, "BackendService",
            cluster=cluster,
            task_definition=task_definition,
            task_definition_revision=ecs.TaskDefinitionRevision.LATEST,
            desired_count=1,
            service_name=self.service_name,
            min_healthy_percent=0,
            max_healthy_percent=100,
        )

        target_group.add_target(service)
from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2
)
from constructs import Construct

class BackendTargetGroupStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Target backend
        self.backend_target_group = elbv2.ApplicationTargetGroup(
            self, "BackendTargetGroup",
            vpc=vpc,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            target_type=elbv2.TargetType.INSTANCE,
            health_check=elbv2.HealthCheck(
                path="/health",
                interval=Duration.seconds(30),
                timeout=Duration.seconds(5),
                healthy_threshold_count=2,
                unhealthy_threshold_count=2
            ),
            target_group_name="backend-tg"
        )

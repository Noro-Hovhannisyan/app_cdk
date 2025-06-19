import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2
)
from constructs import Construct

class TargetGroupStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "tg.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        for tg_conf in config["tgs"]:
            vpc = ec2.Vpc.from_lookup(
                self,
                tg_conf["name"] + "VPC",
                tags={"Name": tg_conf["vpc_name"]},
            )
            tg = elbv2.ApplicationTargetGroup(
            self, "BackendTargetGroup",
            vpc=vpc,
            port=tg_conf["port"],
            protocol=elbv2.ApplicationProtocol(tg_conf["protocol"]),
            target_type=elbv2.TargetType(tg_conf["target_type"]),
            health_check=elbv2.HealthCheck(
                path=tg_conf["path"],
                interval=Duration.seconds(tg_conf["interval"]),
                timeout=Duration.seconds(tg_conf["timeout"]),
                healthy_threshold_count=tg_conf["healthy_threshold_count"],
                unhealthy_threshold_count=tg_conf["unhealthy_threshold_count"],
            ),
            target_group_name=tg_conf["name"],
        )
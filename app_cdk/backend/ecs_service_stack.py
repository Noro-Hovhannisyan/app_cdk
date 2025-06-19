import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2
)
import boto3
from constructs import Construct

class ECSServiceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,task_definitions: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "ecs_service.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        for service_conf in config["services"]:
            vpc = ec2.Vpc.from_lookup(
                self,
                service_conf["name"] + "VPC",
                tags={"Name": service_conf["vpc_name"]},
            )
            cluster = ecs.Cluster.from_cluster_attributes(
                self, service_conf["name"] + "cluster",
                cluster_name=service_conf["cluster_name"],
                vpc=vpc
            )
            # ecs_client = boto3.client("ecs", region_name="eu-north-1")
            # response = ecs_client.list_task_definitions(
            #     familyPrefix=service_conf["family"],
            #     sort="DESC",
            #     maxResults=1
            # )
            # latest_task_def_arn = response["taskDefinitionArns"][0]
            # task_definition = ecs.TaskDefinition.from_task_definition_arn(
            #     self, service_conf["name"] + "td",
            #     task_definition_arn=latest_task_def_arn
            # )
            task_definition = task_definitions[service_conf["task_definition_name"]]
            target_group = elbv2.ApplicationTargetGroup.from_target_group_attributes(
                self, service_conf["name"] + "target_group",
                target_group_arn=service_conf["target_group_arn"],
            )

            service = ecs.Ec2Service(self, service_conf["name"] + "service",
                cluster=cluster,
                task_definition=task_definition,
                task_definition_revision=ecs.TaskDefinitionRevision.LATEST,
                desired_count=service_conf["desired_count"],
                service_name=service_conf["name"],
                min_healthy_percent=service_conf["min_healthy_percent"],
                max_healthy_percent=service_conf["max_healthy_percent"],
            )

            target_group.add_target(service)
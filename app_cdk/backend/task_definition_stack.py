import yaml
from pathlib import Path
from aws_cdk import (
    aws_ecs as ecs,
    Stack,
    aws_iam as iam,
)
from constructs import Construct

class TaskDefStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "task_definition.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.td_map = {}
        for td_conf in config["task_definitions"]:
            # task role
            task_role = iam.Role.from_role_arn(
                self, td_conf["name"]+"role",
                td_conf["role_arn"],
            )

            # Task Definition
            task_def = ecs.Ec2TaskDefinition(self, td_conf["name"]+"-td",
                                                  family=td_conf["name"],
                                                  network_mode=ecs.NetworkMode(td_conf["network_mode"]),
                                                  task_role=task_role,
                                                  execution_role=task_role,
                                                  )

            # container
            container = task_def.add_container(td_conf["name"]+"-container",
                                                    image=ecs.ContainerImage.from_registry(
                                                        td_conf["image"]),
                                                    memory_limit_mib=td_conf["memory_limit_mib"],
                                                    cpu=td_conf["cpu"],
                                                    )

            # port
            container.add_port_mappings(
                ecs.PortMapping(
                    container_port=td_conf["container_port"],
                    host_port=td_conf["host_port"],
                    protocol=ecs.Protocol(td_conf["protocol"]),
                    name=td_conf["port_name"],
                    app_protocol=ecs.AppProtocol(td_conf["app_protocol"]),
                )
            )
            self.td_map[td_conf["name"]] = task_def

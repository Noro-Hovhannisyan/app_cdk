import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_iam as iam,
)
from constructs import Construct

class EcrStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "ecr.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        for ecr_conf in config["repos"]:
            repo = ecr.Repository(
                self, ecr_conf["name"],
                repository_name=ecr_conf["name"],
            )
            repo.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=ecr_conf["actions"],
            )
        )


#============            Old Version   =============
        # # ECR backend
        # repo = ecr.Repository(
        #     self, "EcrRepo",
        #     repository_name="backend",
        # )
        #
        #
        # repo.add_to_resource_policy(
        #     iam.PolicyStatement(
        #         effect=iam.Effect.ALLOW,
        #         principals=[iam.AnyPrincipal()],
        #         actions=[
        #             "ecr:GetDownloadUrlForLayer",
        #             "ecr:BatchGetImage",
        #             "ecr:BatchCheckLayerAvailability"
        #         ]
        #     )
        # )




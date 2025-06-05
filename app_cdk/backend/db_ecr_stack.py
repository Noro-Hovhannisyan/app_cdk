from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_iam as iam,
)
from constructs import Construct

class DBEcrStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ECR DB
        repo = ecr.Repository(
            self, "EcrRepo",
            repository_name="db",
        )


        repo.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=[
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "ecr:BatchCheckLayerAvailability"
                ]
            )
        )
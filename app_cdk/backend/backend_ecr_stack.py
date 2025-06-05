from aws_cdk import (
    Stack,
    aws_ecr as ecr,
    aws_iam as iam,
)
from constructs import Construct

class EcrStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # ECR backend
        repo = ecr.Repository(
            self, "EcrRepo",
            repository_name="backend",
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




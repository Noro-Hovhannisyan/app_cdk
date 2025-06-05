from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
)
from constructs import Construct

class LambdaCdnInvalidationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, distribution_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.invalidation_lambda = _lambda.Function(self, "InvalidationLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="cdn_invalidator.handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(30),
            environment={
                "DISTRIBUTION_ID": distribution_id
            }
        )

        # Allow Lambda to invalidate CloudFront
        self.invalidation_lambda.add_to_role_policy(iam.PolicyStatement(
            actions=["cloudfront:CreateInvalidation"],
            resources=["*"]
        ))
        # Allow S3 to invoke Lambda
        self.invalidation_lambda.add_permission(
            "AllowS3Invoke",
            principal=iam.ServicePrincipal("s3.amazonaws.com"),
            action="lambda:InvokeFunction",
            source_arn = "arn:aws:s3:::*"
        )


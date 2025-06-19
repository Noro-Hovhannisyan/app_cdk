import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_s3_notifications as s3n
)
from constructs import Construct

class LambdaCdnInvalidationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "lambda.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.lambda_map = {}
        for lambda_conf in config["functions"]:
            lambdafun = _lambda.Function(self, lambda_conf["name"],
                                         function_name=lambda_conf["name"],
                                         runtime=getattr(_lambda.Runtime, lambda_conf["runtime"]),
                                         handler=lambda_conf["handler"],
                                         code=_lambda.Code.from_asset(lambda_conf["folder"]),
                                         timeout=Duration.seconds(lambda_conf["timeout"]),
                                         environment=lambda_conf["environment"]
                                         )
            lambdafun.add_to_role_policy(iam.PolicyStatement(
                actions=lambda_conf["actions"],
                resources=lambda_conf["resources"],
            ))

            lambdafun.add_permission(
                lambda_conf["name"]+"permission",
                principal=iam.ServicePrincipal(lambda_conf["principal"]),
                action=lambda_conf["action"],
                source_arn=lambda_conf["source_arn"],
            )
            self.lambda_map[lambda_conf["name"]] = lambdafun


























#         ============= Old Version =============
# class LambdaCdnInvalidationStack(Stack):
#     def __init__(self, scope: Construct, construct_id: str, distribution_id: str, **kwargs) -> None:
#         super().__init__(scope, construct_id, **kwargs)
#
#         self.invalidation_lambda = _lambda.Function(self, "InvalidationLambda",
#             runtime=_lambda.Runtime.PYTHON_3_12,
#             handler="cdn_invalidator.handler",
#             code=_lambda.Code.from_asset("lambda"),
#             timeout=Duration.seconds(30),
#             environment={
#                 "DISTRIBUTION_ID": distribution_id
#             }
#         )
#
#         # Allow Lambda to invalidate CloudFront
#         self.invalidation_lambda.add_to_role_policy(iam.PolicyStatement(
#             actions=["cloudfront:CreateInvalidation"],
#             resources=["*"]
#         ))
#         # Allow S3 to invoke Lambda
#         self.invalidation_lambda.add_permission(
#             "AllowS3Invoke",
#             principal=iam.ServicePrincipal("s3.amazonaws.com"),
#             action="lambda:InvokeFunction",
#             source_arn = "arn:aws:s3:::*"
#         )


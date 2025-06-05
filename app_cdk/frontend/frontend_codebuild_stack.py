from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_iam as iam,
)
from constructs import Construct

class CodeBuildFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, repo: codecommit.IRepository,  **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # === 1. Inline IAM Policy ===
        s3_policy = iam.PolicyDocument(statements=[
            iam.PolicyStatement(
                actions=[
                    "s3:PutObject",
                    "s3:GetObject",
                    "s3:DeleteObject",
                    "s3:ListBucket"
                ],
                resources=[
                    "arn:aws:s3:::frontend-react-713767909258",
                    "arn:aws:s3:::frontend-react-713767909258/*"
                ]
            )
        ])

        # === 2. Create IAM Role for CodeBuild ===
        codebuild_role = iam.Role(
            self, "CodeBuildFrontendRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            inline_policies={
                "S3AccessPolicy": s3_policy
            }
        )

        self.project = codebuild.Project(self,"CodeBuildFrontend",
            project_name = "frontend",
            role=codebuild_role,
            source = codebuild.Source.code_commit(
                repository=repo,
                branch_or_ref="master"
            ),
            build_spec = codebuild.BuildSpec.from_source_filename("buildspec.yml"),
        )
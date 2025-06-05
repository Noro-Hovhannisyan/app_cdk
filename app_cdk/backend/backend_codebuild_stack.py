from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_iam as iam,
)
from constructs import Construct

class CodeBuildBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, repo: codecommit.IRepository, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # === 2. Create IAM Role for CodeBuild ===
        codebuild_role = iam.Role(
            self, "BackendCodeBuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com")
        )

        # === 3. Attach ECR permissions to the CodeBuild role ===
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "ecr:GetAuthorizationToken",  # Allow authentication with ECR
                    "ecr:BatchGetImage",  # Allow pulling images from ECR
                    "ecr:BatchCheckLayerAvailability",  # Allow checking layer availability
                    "ecr:InitiateLayerUpload",  # Allow initiating layer upload (for pushing images)
                    "ecr:UploadLayerPart",  # Allow uploading image layers (for pushing images)
                    "ecr:CompleteLayerUpload",  # Allow completing layer upload (for pushing images)
                    "ecr:PutImage"  # Разрешение на загрузку образа в ECR
                ],
                resources=["*"]  # You can restrict this to specific repositories if needed
            )
        )

        # === 4. Create the CodeBuild Project ===
        self.project = codebuild.Project(self, "CodeBuildBackend",
            project_name="backend",
            role=codebuild_role,
            source=codebuild.Source.code_commit(
                repository=repo,
                branch_or_ref="master"
            ),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
        )

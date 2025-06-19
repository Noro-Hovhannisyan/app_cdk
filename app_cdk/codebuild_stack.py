import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codecommit as codecommit,
    aws_iam as iam,
)
from constructs import Construct

class CodeBuildStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent / "configs" / "codebuild.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        for project_conf in config["projects"]:
            # === 1. Create IAM Role for CodeBuild ===
            codebuild_role = iam.Role(
            self, project_conf["name"]+"role",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com")
            )
            # === 2. Attach permissions to the CodeBuild role ===
            codebuild_role.add_to_policy(
                iam.PolicyStatement(
                    actions=project_conf["actions"],
                    resources=project_conf["resources"],
                )
            )
            # === 3. Getting Repo
            repo = codecommit.Repository.from_repository_name(
                self, project_conf["repo_name"]+"repo", project_conf["repo_name"]
            )
            # === 4. Create the CodeBuild Project ===
            project = codebuild.Project(self, project_conf["name"],
                project_name=project_conf["name"],
                role=codebuild_role,
                source=codebuild.Source.code_commit(
                    repository=repo,
                    branch_or_ref=project_conf["branch_or_ref"],
                ),
                build_spec=codebuild.BuildSpec.from_source_filename(project_conf["build_spec"]),
            )
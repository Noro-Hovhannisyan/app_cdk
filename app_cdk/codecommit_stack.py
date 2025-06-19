import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
)
from constructs import Construct

class CodeCommitStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent / "configs" / "codecommit.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.repos = {}

        for repo_conf in config["repos"]:
            repo = codecommit.Repository(self, repo_conf["name"],
            repository_name=repo_conf["name"]
            )
            self.repos[repo_conf["name"]] = repo


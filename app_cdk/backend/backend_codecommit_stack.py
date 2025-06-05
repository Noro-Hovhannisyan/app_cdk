from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
)
from constructs import Construct

class CodeCommitBackendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.repo = codecommit.Repository(self, "CodeCommitBackend",
            repository_name="backend"
        )


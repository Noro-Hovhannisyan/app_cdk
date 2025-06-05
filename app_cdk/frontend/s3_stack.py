from aws_cdk import (
    Stack,
    aws_s3 as s3,
    Aws,
    RemovalPolicy
)
from constructs import Construct

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        acc_id = Aws.ACCOUNT_ID
        self.front_bucket = s3.Bucket(self, "front-bucket",
            bucket_name="frontend-react-"+str(acc_id),
            block_public_access=s3.BlockPublicAccess(block_public_acls=False,
                                             ignore_public_acls=False,
                                             restrict_public_buckets=False,
                                             block_public_policy=False),
            public_read_access=True,
            website_index_document="index.html",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        self.frontend_artifact_bucket = s3.Bucket(self, "FrontendArtifactBucket")
        self.backend_artifact_bucket = s3.Bucket(self, "BackendArtifactBucket")



import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    Aws,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_s3_notifications as s3n
)
from constructs import Construct

class S3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        acc_id = Aws.ACCOUNT_ID

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "s3.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.s3_map = {}
        for s3_conf in config["s3_buckets"]:

            s3_bucket = s3.Bucket(self, s3_conf["name"],
                                  bucket_name=s3_conf["name"]+"-"+str(acc_id),
                                  block_public_access=s3.BlockPublicAccess(
                                      block_public_acls=s3_conf["block_public_acls"],
                                      ignore_public_acls=s3_conf["ignore_public_acls"],
                                      restrict_public_buckets=s3_conf["restrict_public_buckets"],
                                      block_public_policy=s3_conf["block_public_policy"],
                                  ),
                                  public_read_access=s3_conf["public_read_access"],
                                  website_index_document=s3_conf.get("website_index_document", None),
                                  removal_policy=RemovalPolicy[s3_conf["removal_policy"]],
                                  auto_delete_objects=s3_conf["auto_delete_objects"],
                                  )
            if "notification" in s3_conf:
                for not_conf in s3_conf["notification"]:

                    lambda_fn = _lambda.Function.from_function_name(
                        self,
                        not_conf["lambda_name"],
                        function_name=not_conf["lambda_name"],
                    )
                    s3_bucket.add_event_notification(
                        s3.EventType.OBJECT_CREATED,
                        s3n.LambdaDestination(lambda_fn),
                        s3.NotificationKeyFilter(suffix=not_conf["suffix"]),
                    )

            self.s3_map[s3_conf["name"]] = s3_bucket


        # ---------- OLD version -----------
        # self.front_bucket = s3.Bucket(self, "front-bucket",
        #     bucket_name="frontend-react-"+str(acc_id),
        #     block_public_access=s3.BlockPublicAccess(block_public_acls=False,
        #                                      ignore_public_acls=False,
        #                                      restrict_public_buckets=False,
        #                                      block_public_policy=False),
        #     public_read_access=True,
        #     website_index_document="index.html",
        #     removal_policy=RemovalPolicy.DESTROY,
        #     auto_delete_objects=True
        # )
        #
        # self.frontend_artifact_bucket = s3.Bucket(self, "FrontendArtifactBucket")
        # self.backend_artifact_bucket = s3.Bucket(self, "BackendArtifactBucket")



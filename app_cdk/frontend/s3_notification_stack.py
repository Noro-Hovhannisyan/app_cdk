# app_cdk/s3_notifications_stack.py

from aws_cdk import Stack, aws_s3 as s3, aws_s3_notifications as s3n
from constructs import Construct

class S3NotificationsStack(Stack):
    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, lambda_fn, **kwargs):
        super().__init__(scope, id, **kwargs)

        bucket.add_event_notification(
            s3.EventType.OBJECT_CREATED,
            s3n.LambdaDestination(lambda_fn),
            s3.NotificationKeyFilter(suffix="index.html")
        )

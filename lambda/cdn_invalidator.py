import boto3
import os
import json

def handler(event, context):
    client = boto3.client('cloudfront')

    distribution_id = os.environ['DISTRIBUTION_ID']
    paths = ['/*']

    response = client.create_invalidation(
        DistributionId=distribution_id,
        InvalidationBatch={
            'Paths': {
                'Quantity': len(paths),
                'Items': paths
            },
            'CallerReference': str(context.aws_request_id)
        }
    )

    print("Invalidation submitted:", json.dumps(response, indent=2))
    return {
        "statusCode": 200,
        "body": "Invalidation triggered"
    }
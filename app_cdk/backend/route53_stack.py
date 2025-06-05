from aws_cdk import (
    aws_route53 as route53,
    Stack,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53_targets as targets,
    aws_cloudfront as cloudfront,

)
from constructs import Construct

class Route53Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, alb: elbv2.ApplicationLoadBalancer, cdn: cloudfront.Distribution,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Hosted Zone
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "MyZone",
            hosted_zone_id="Z03054271SZN0HSASJEI7",
            zone_name="academy.goya.am"
        )

        # ALB record
        route53.ARecord(self, "FlaskAliasRecord",
            zone=hosted_zone,
            record_name="flask",
            target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(alb))
        )

        # CDN record
        route53.ARecord(self, "ReactAliasRecord",
            zone=hosted_zone,
            record_name="react",
            target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(cdn))
        )



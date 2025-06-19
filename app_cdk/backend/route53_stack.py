import yaml
from pathlib import Path
from aws_cdk import (
    aws_route53 as route53,
    Stack,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53_targets as targets,
    aws_cloudfront as cloudfront,

)
from constructs import Construct

class Route53Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "route53.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        for record_conf in config["records"]:
            if record_conf["target_type"] == "alb":


                alb = elbv2.ApplicationLoadBalancer.from_application_load_balancer_attributes(
                    self,
                    record_conf["name"]+"alb",
                    load_balancer_arn=record_conf["load_balancer_arn"],
                    security_group_id=record_conf["security_group_id"],
                    load_balancer_canonical_hosted_zone_id=record_conf["load_balancer_canonical_hosted_zone_id"],
                    load_balancer_dns_name=record_conf["load_balancer_dns_name"],
                    )

                hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, record_conf["name"]+"hostedzone",
                                                                             hosted_zone_id=record_conf["hosted_zone_id"],
                                                                             zone_name=record_conf["zone_name"]
                                                                             )
                route53.ARecord(self, "FlaskAliasRecord",
                                zone=hosted_zone,
                                record_name=record_conf["name"],
                                target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(alb))
                                )
            elif record_conf["target_type"] == "cdn":
                cdn = cloudfront.Distribution.from_distribution_attributes(
                    self,
                    record_conf["name"]+"cdn",
                    domain_name=record_conf["domain_name"],
                    distribution_id=record_conf["distribution_id"],
                )
                hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, record_conf["name"] + "hostedzone",
                                                                             hosted_zone_id=record_conf[
                                                                                 "hosted_zone_id"],
                                                                             zone_name=record_conf["zone_name"]
                                                                             )
                route53.ARecord(self, "ReactAliasRecord",
                                zone=hosted_zone,
                                record_name=record_conf["name"],
                                target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(cdn))
                                )


        # # ====== Old Version =======
        # # Hosted Zone
        # hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "MyZone",
        #     hosted_zone_id="Z03054271SZN0HSASJEI7",
        #     zone_name="academy.goya.am"
        # )
        #
        # # ALB record
        # route53.ARecord(self, "FlaskAliasRecord",
        #     zone=hosted_zone,
        #     record_name="flask",
        #     target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(alb))
        # )
        #
        # # CDN record
        # route53.ARecord(self, "ReactAliasRecord",
        #     zone=hosted_zone,
        #     record_name="react",
        #     target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(cdn))
        # )



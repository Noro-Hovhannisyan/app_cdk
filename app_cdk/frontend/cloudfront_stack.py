import yaml
from pathlib import Path
from aws_cdk import (
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3 as s3,
    Stack,
    aws_certificatemanager as acm,
    aws_route53 as route53,
)
from constructs import (Construct)

class CdnStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope,construct_id,**kwargs)

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "cdn.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.distributions = {}
        for cdn_conf in config["distributions"]:
            if "acm" in cdn_conf:
                acm_conf = cdn_conf["acm"]
                # Hosted Zone
                hosted_zone = route53.HostedZone.from_hosted_zone_attributes(
                    self, acm_conf["hosted_zone_id"],
                    hosted_zone_id=acm_conf["hosted_zone_id"],
                    zone_name=acm_conf["zone_name"]
                )

                # ACM
                certificate = acm.DnsValidatedCertificate(
                    self, acm_conf["acm_id"],
                    domain_name=acm_conf["domain_name"],
                    hosted_zone=hosted_zone,
                    region=acm_conf["region"],
                )
            cdn = cloudfront.Distribution(
                self, cdn_conf["name"],
                default_behavior=cloudfront.BehaviorOptions(
                    origin=origins.S3Origin(bucket),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy[cdn_conf["viewer_protocol_policy"]],
                ),
                default_root_object=cdn_conf.get("default_root_object", None),
                certificate=certificate,
                domain_names=cdn_conf.get("domain_names", []),
            )


        # -------------- old version ----------------------
        # # Hosted Zone
        # hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "MyZone",
        #                                                              hosted_zone_id="Z03054271SZN0HSASJEI7",
        #                                                              zone_name="academy.goya.am"
        #                                                              )
        # # ACM
        # certificate = acm.DnsValidatedCertificate(
        #     self, "CDNCertificate",
        #     domain_name="react.academy.goya.am",
        #     hosted_zone=hosted_zone,
        #     region="us-east-1",
        # )
        #
        # # CDN
        # self.cloudfront = cloudfront.Distribution(self, "Cloudfront",
        #
        #
        #         default_behavior=cloudfront.BehaviorOptions(
        #             origin=origins.S3Origin(bucket),
        #             viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
        #     ),
        #         default_root_object="index.html",
        #         certificate=certificate,
        #         domain_names=["react.academy.goya.am"],
        #     )

from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_certificatemanager as acm, Duration,
)
from aws_cdk.aws_elasticloadbalancingv2 import ListenerAction
from constructs import Construct




class LoadBalancerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc,backend_tg,alb_sg, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # ALB
        self.alb = elbv2.ApplicationLoadBalancer(self, "BackendALB",
            vpc=vpc,
            security_group=alb_sg,
            internet_facing=True,
            load_balancer_name="task-alb"
        )


        # Hosted Zone
        hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "MyZone",
            hosted_zone_id="Z03054271SZN0HSASJEI7",
            zone_name="academy.goya.am"
        )

        # ACM
        certificate = acm.DnsValidatedCertificate(
            self, "SiteCertificate",
            domain_name="flask.academy.goya.am",
            hosted_zone=hosted_zone,
            region="eu-north-1",
        )

        # HTTPS Listener
        self.listener_https = self.alb.add_listener("HttpsListener",
            port=443,
            certificates=[certificate],
            default_target_groups=[backend_tg]
        )


        # HTTP Listener
        self.listener_http = self.alb.add_listener("HttpListener", port=80)




        self.listener_http.add_action("ToHttpsListener",
            action=elbv2.ListenerAction.redirect(
                protocol="HTTPS",
                port="443",
            )
        )






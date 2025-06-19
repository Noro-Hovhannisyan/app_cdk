import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_certificatemanager as acm, Duration,
)
from constructs import Construct




class LoadBalancerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "alb.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        for lb_conf in config["balancers"]:
            vpc = ec2.Vpc.from_lookup(
                self,
                lb_conf["name"] + "VPC",
                tags={"Name": lb_conf["vpc_name"]},
            )
            sg = ec2.SecurityGroup.from_security_group_id(
                self,
                lb_conf["name"] + "SG",
                security_group_id=lb_conf["sg_id"],
            )
            # LB
            lb = elbv2.ApplicationLoadBalancer(self, lb_conf["name"]+"lb",
                                               vpc=vpc,
                                               security_group=sg,
                                               internet_facing=lb_conf["internet_facing"],
                                               load_balancer_name=lb_conf["name"]
                                               )

            for listener_conf in lb_conf["listeners"]:
                if "hosted_zone_id" in listener_conf:
                    tg = elbv2.ApplicationTargetGroup.from_target_group_attributes(
                        self, lb_conf["name"] + "tg",
                        target_group_arn=listener_conf["target_group_arn"],
                    )
                    # Hosted Zone
                    hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, lb_conf["name"]+"HostedZone",
                                                                                 hosted_zone_id=listener_conf["hosted_zone_id"],
                                                                                 zone_name=listener_conf["zone_name"]
                                                                                 )
                    # ACM
                    certificate = acm.DnsValidatedCertificate(
                        self, lb_conf["name"] + "Certificate",
                        domain_name=listener_conf["domain_name"],
                        hosted_zone=hosted_zone,
                        region=listener_conf["region"],
                    )
                    listener = lb.add_listener(str(listener_conf["port"]) + "Listener",
                                               port=listener_conf["port"],
                                               certificates=[certificate],
                                               default_target_groups=[tg]
                    )
                else:
                    listener = lb.add_listener(str(listener_conf["port"]) + "Listener",
                                               port=listener_conf["port"],)

                    listener.add_action(str(listener_conf["port"]) + "Action",
                                        action=elbv2.ListenerAction.redirect(
                                            protocol=listener_conf["protocol"],
                                            port=listener_conf["action_port"],
                                        )
                                        )







        # ====== Old Version ======
        # # ALB
        # self.alb = elbv2.ApplicationLoadBalancer(self, "BackendALB",
        #     vpc=vpc,
        #     security_group=alb_sg,
        #     internet_facing=True,
        #     load_balancer_name="task-alb"
        # )
        #
        #
        # # Hosted Zone
        # hosted_zone = route53.HostedZone.from_hosted_zone_attributes(self, "MyZone",
        #     hosted_zone_id="Z03054271SZN0HSASJEI7",
        #     zone_name="academy.goya.am"
        # )
        #
        # # ACM
        # certificate = acm.DnsValidatedCertificate(
        #     self, "SiteCertificate",
        #     domain_name="flask.academy.goya.am",
        #     hosted_zone=hosted_zone,
        #     region="eu-north-1",
        # )
        #
        # # HTTPS Listener
        # self.listener_https = self.alb.add_listener("HttpsListener",
        #     port=443,
        #     certificates=[certificate],
        #     default_target_groups=[backend_tg]
        # )
        #
        #
        # # HTTP Listener
        # self.listener_http = self.alb.add_listener("HttpListener", port=80)
        #
        #
        #
        #
        # self.listener_http.add_action("ToHttpsListener",
        #     action=elbv2.ListenerAction.redirect(
        #         protocol="HTTPS",
        #         port="443",
        #     )
        # )






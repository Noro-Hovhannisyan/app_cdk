import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_ssm as ssm,
)
from constructs import Construct

class SecurityStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "sg.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)


        self.sg_map = {}
        for sg_conf in config["security_groups"]:
            sg = ec2.SecurityGroup(
                self, sg_conf["name"],
                vpc=vpc,
                security_group_name = sg_conf["name"],
                description = sg_conf["description"],
                allow_all_outbound = sg_conf.get("allow_all_outbound", True)
            )
            self.sg_map[sg_conf["name"]] = sg

        for sg_conf in config["security_groups"]:
            current = self.sg_map[sg_conf["name"]]
            for rule in sg_conf["ingress"]:
                if "cidr" in rule:
                    peer = ec2.Peer.ipv4(rule["cidr"])
                elif "src" in rule:
                    peer = self.sg_map[rule["src"]]
                else:
                    raise ValueError("No valid src name or cidr")
                current.add_ingress_rule(peer, ec2.Port.tcp_range(rule["start_port"], rule["end_port"]),rule["description"])

        for sg_conf in config["add_rules"]:
            current = self.sg_map[sg_conf["name"]]
            for rule in sg_conf["ingress"]:
                if "cidr" in rule:
                    peer = ec2.Peer.ipv4(rule["cidr"])
                elif "src" in rule:
                    peer = self.sg_map[rule["src"]]
                else:
                    raise ValueError("No valid src name or cidr")
                current.add_ingress_rule(peer, ec2.Port.tcp_range(rule["start_port"], rule["end_port"]),rule["description"])






        #----------------old version--------------------
        # # ALB
        # self.alb_sg = ec2.SecurityGroup(self, 'alb_sg',
        #     security_group_name='alb_sg',
        #     vpc=vpc,
        #     allow_all_outbound=True,
        #     description='ALB Security Group'
        # )
        #     # inbound
        # self.alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP")
        # self.alb_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "HTTPS")
        #
        #     # outbound
        # self.alb_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_traffic())
        #
        # # Cluster
        # self.ecs_ec2_cluster_sg = ec2.SecurityGroup(self, "ecs-ec2-cluster-sg",
        #     security_group_name="ecs-ec2-cluster-sg",
        #     vpc=vpc,
        #     allow_all_outbound=True,
        #     description="Security Group for ECS Cluster",
        # )
        #     # inbound
        # self.ecs_ec2_cluster_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH to ECS Cluster")
        # self.ecs_ec2_cluster_sg.add_ingress_rule(self.alb_sg, ec2.Port.tcp_range(32768,60999), "To ECS Cluster from ALB")
        #
        # # self.ecs_ec2_cluster_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_traffic(),"Test")
        #     # outbound
        # self.ecs_ec2_cluster_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_traffic())
        #
        # # DB
        # self.db_sg = ec2.SecurityGroup(self, "db_sg",
        #     security_group_name="db_sg",
        #     vpc=vpc,
        #     allow_all_outbound=True,
        #     description="DB Security Group",
        # )
        #     # inbound
        # self.db_sg.add_ingress_rule(self.ecs_ec2_cluster_sg, ec2.Port.tcp(5432), "Back to DB")
        # # self.db_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_traffic(),"test")
        #
        #     # outbound
        # self.ecs_ec2_cluster_sg.add_egress_rule(ec2.Peer.any_ipv4(), ec2.Port.all_traffic())
        #
        # # Backend
        #     # inbound
        # self.ecs_ec2_cluster_sg.add_ingress_rule(self.db_sg, ec2.Port.tcp_range(32768, 60999), "DB to Back")
import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class VpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "vpc.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        self.vpc_map = {}
        for vpc_conf in config["all_vpc"]:
            subnet_config = []
            for subnet in vpc_conf["subnet-configuration"]:
                subnet_config.append(
                    ec2.SubnetConfiguration(
                        name=subnet["name"],
                        subnet_type=ec2.SubnetType[subnet["subnet_type"]],
                        cidr_mask=subnet["cidr_mask"],
                    )
                )
            vpc = ec2.Vpc(self,vpc_conf["name"],
                vpc_name=vpc_conf["name"],
                ip_addresses=ec2.IpAddresses.cidr(vpc_conf["cidr"]),
                nat_gateways=vpc_conf["nat_gateways"],
                max_azs=vpc_conf["max_azs"],
                subnet_configuration=subnet_config,
            )
            self.vpc_map[vpc_conf["name"]] = vpc








        # for vpc in config["vpc"]:
        #     vpc_config = config["vpc"]
        #     subnet_public_config = vpc_config["subnet-public"]
        #     subnet_private_config = vpc_config["subnet-private"]
        #     subnet_isolated_config = vpc_config["subnet-isolated"]
        #     self.vpc = ec2.Vpc(self,'vpc',
        #         vpc_name=vpc_config["vpc_name"],
        #         cidr=vpc_config["cidr"],
        #         nat_gateways=vpc_config["nat_gateways"],
        #         max_azs=vpc_config["max_azs"],
        #         subnet_configuration=[
        #             ec2.SubnetConfiguration(
        #                 name=subnet_public_config["name"],
        #                 subnet_type=ec2.SubnetType[subnet_public_config["subnet_type"]],
        #                 cidr_mask=subnet_public_config["cidr_mask"],
        #             ),
        #             ec2.SubnetConfiguration(
        #                 name=subnet_private_config["name"],
        #                 subnet_type=ec2.SubnetType[subnet_private_config["subnet_type"]],
        #                 cidr_mask=subnet_private_config["cidr_mask"],
        #             ),
        #             ec2.SubnetConfiguration(
        #                 name=subnet_isolated_config["name"],
        #                 subnet_type=ec2.SubnetType[subnet_isolated_config["subnet_type"]],
        #                 cidr_mask=subnet_isolated_config["cidr_mask"],
        #             )
        #         ]
        #     )

        #----------------old version--------------------
        # self.vpc = ec2.Vpc(self,'vpc',
        #     vpc_name='task_vpc',
        #     cidr='192.168.0.0/16',
        #     nat_gateways=0,
        #     max_azs=3,
        #     subnet_configuration=[
        #         ec2.SubnetConfiguration(
        #             name='public-subnet',
        #             subnet_type=ec2.SubnetType.PUBLIC,
        #             cidr_mask=24
        #         ),
        #         ec2.SubnetConfiguration(
        #             name='private-subnet',
        #             subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
        #             cidr_mask=24
        #         ),
        #         ec2.SubnetConfiguration(
        #             name='isolated-subnet',
        #             subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
        #             cidr_mask=24
        #         )
        #     ]
        # )




import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct

class Ec2InstanceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "ec2.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        for ec2_conf in config["instances"]:
            vpc = ec2.Vpc.from_lookup(
                self,
                ec2_conf["name"] + "VPC",
                tags={"Name": ec2_conf["vpc_name"]},
            )
            sg = ec2.SecurityGroup.from_security_group_id(
                self,
                ec2_conf["name"] + "SG",
                security_group_id=ec2_conf["sg_id"],
            )
            role = iam.Role(self, ec2_conf["name"]+"role",
                            assumed_by=iam.ServicePrincipal(ec2_conf["assumed_by"]),
                            managed_policies=[
                                iam.ManagedPolicy.from_aws_managed_policy_name(ec2_conf["managed_policies"]),
                            ]
                            )

            ami = ec2.MachineImage.generic_linux({
                ec2_conf["region"]: ec2_conf["ami"]
            })

            # EC2 instance
            ec2.Instance(self, ec2_conf["name"]+"instance",
                         instance_name=ec2_conf["name"],
                         instance_type=ec2.InstanceType(ec2_conf["instance_type"]),
                         machine_image=ami,
                         vpc=vpc,
                         security_group=sg,
                         vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType(ec2_conf["subnet_type"])),
                         role=role,
                         key_name=ec2_conf["key_name"],
                         block_devices=[
                             ec2.BlockDevice(
                                 device_name=ec2_conf["device_name"],
                                 volume=ec2.BlockDeviceVolume.ebs(
                                     volume_size=ec2_conf["volume_size"],
                                     encrypted=ec2_conf["encrypted"],
                                 )
                             )
                         ]
                         )


from aws_cdk import (
    App, Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
)
from constructs import Construct

class DbEc2InstanceStack(Stack):
     def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc,db_sg,**kwargs):
        super().__init__(scope, construct_id, **kwargs)

        role = iam.Role(self, "SSMRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )

        ami = ec2.MachineImage.generic_linux({
            "eu-north-1": "ami-09516355bded22b02"
        })



        # EC2 instance
        ec2.Instance(self, "DbInstance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ami,
            vpc=vpc,
            security_group=db_sg,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            role=role,
            key_name="EC2 Tutorial",
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(
                        volume_size=20,
                        encrypted=True
                    )
                )
            ]
        )

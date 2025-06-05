from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
)
from constructs import Construct

class VpcStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.vpc = ec2.Vpc(self,'vpc',
            vpc_name='task_vpc',
            cidr='192.168.0.0/16',
            nat_gateways=0,
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='public-subnet',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name='private-subnet',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name='isolated-subnet',
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )


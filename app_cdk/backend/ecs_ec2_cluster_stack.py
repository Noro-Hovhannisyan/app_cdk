import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_autoscaling as autoscaling,
    RemovalPolicy
)

from constructs import Construct

class EcsClusterStack(Stack):
    def __init__(self, scope: Construct, construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "cluster.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)


        self.cluster_map = {}
        for cluster_conf in config["clusters"]:
            vpc = ec2.Vpc.from_lookup(
                self,
                cluster_conf["name"] + "VPC",
                tags={"Name": cluster_conf["vpc_name"]},
            )
            sg = ec2.SecurityGroup.from_security_group_id(
                self,
                cluster_conf["name"] + "SG",
                security_group_id=cluster_conf["sg_id"],
            )
            # 1. Creating Cluster
            cluster = ecs.Cluster(self, cluster_conf["name"], vpc=vpc,cluster_name=cluster_conf["name"])
            # 2. EC2 Instance Role
            existing_role = iam.Role.from_role_arn(self, cluster_conf["name"]+"role", cluster_conf["role_arn"])
            # 3. ASG
            asg = autoscaling.AutoScalingGroup(self, cluster_conf["name"]+"asg",
            vpc=vpc,
            instance_type=ec2.InstanceType(cluster_conf["instance_type"]),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            min_capacity=cluster_conf["min_capacity"],
            max_capacity=cluster_conf["max_capacity"],
            role=existing_role,
            key_name=cluster_conf["key_name"],
            security_group=sg,
            associate_public_ip_address=cluster_conf["associate_public_ip_address"],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType(cluster_conf["subnet_type"]))
            )
            # 4. Capacity Provider
            capacity_provider = ecs.AsgCapacityProvider(self, cluster_conf["name"] + "CP",
                                                        auto_scaling_group=asg,
                                                        capacity_provider_name=cluster_conf["capacity_provider_name"],
                                                        enable_managed_scaling=cluster_conf["enable_managed_scaling"],
                                                        enable_managed_termination_protection=cluster_conf["enable_managed_termination_protection"],
                                                        machine_image_type=ecs.MachineImageType.AMAZON_LINUX_2
                                                        )
            cluster.add_asg_capacity_provider(capacity_provider)
            # Deleting
            asg.apply_removal_policy(RemovalPolicy.DESTROY)
            cluster.apply_removal_policy(RemovalPolicy.DESTROY)




        # =============== Old Version ===============
        # Создаем ECS кластер
        # self.cluster_name = "ecs-ec2-cluster"
        # self.ecs_cluster = ecs.Cluster(self, "MyEcsCluster", vpc=vpc,cluster_name=self.cluster_name)
        #
        # # EC2 Instance Role
        # existing_role = iam.Role.from_role_arn(self, "ExistingRole", "arn:aws:iam::713767909258:instance-profile/ECS-EC2-Cluster-8")
        #
        #
        #
        # # Создание Auto Scaling группы для EC2 инстансов в ECS
        # asg = autoscaling.AutoScalingGroup(self, "MyEcsAsg",
        #     vpc=vpc,
        #     instance_type=ec2.InstanceType("t3.micro"),
        #     machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
        #     min_capacity=1,
        #     max_capacity=5,
        #     role=existing_role,
        #     key_name="EC2 Tutorial",
        #     security_group=sg,
        #     associate_public_ip_address=True,
        #     vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        # )
        #
        # # Capacity Provider
        # capacity_provider = ecs.AsgCapacityProvider(self, "MyCapacityProvider",
        #     auto_scaling_group=asg,
        #     capacity_provider_name="my-capacity-provider",
        #     enable_managed_scaling=False,
        #     enable_managed_termination_protection=False,
        #     machine_image_type=ecs.MachineImageType.AMAZON_LINUX_2
        # )
        #
        #
        # self.ecs_cluster.add_asg_capacity_provider(capacity_provider)
        #
        # # Deleting
        # asg.apply_removal_policy(RemovalPolicy.DESTROY)
        # self.ecs_cluster.apply_removal_policy(RemovalPolicy.DESTROY)
        #
        # self.cluster = self.ecs_cluster
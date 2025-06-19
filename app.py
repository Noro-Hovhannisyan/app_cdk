#!/usr/bin/env python3


import aws_cdk as cdk
from aws_cdk import  Environment

# ========================== Frontend ==========================
from app_cdk.frontend.vpc_stack import VpcStack
from app_cdk.frontend.sg_stack import SecurityStack
from app_cdk.frontend.s3_stack import S3Stack
from app_cdk.frontend.cloudfront_stack import CdnStack
from app_cdk.codecommit_stack import CodeCommitStack
from app_cdk.codebuild_stack import CodeBuildStack
from app_cdk.pipeline_stack import PipelineStack
from app_cdk.frontend.lambda_cdn_invalidator_stack import LambdaCdnInvalidationStack

app = cdk.App()
# VPC
task_vpc = VpcStack(app, "VpcStack")
# SG
sg = SecurityStack(app, "SecurityStack", task_vpc.vpc_map["task_vpc"])
# S3
s3 = S3Stack(app, "S3Stack")
# CDN
cdn = CdnStack(app, "CdnStack",s3.s3_map["frontend-react"])
# CodeCommit
repo = CodeCommitStack(app, "CodeCommitStack")
# CodeBuild
project = CodeBuildStack(app, "CodeBuildStack")
# Pipeline
pipeline = PipelineStack(app, "PipelineStack",env=Environment(account="713767909258", region="eu-north-1"))
# Lambda
lambdafun = LambdaCdnInvalidationStack(app, "LambdaCdnInvalidationStack")
# ==============================================================================


# ========================== Backend ==========================
from app_cdk.backend.ecr_stack import EcrStack
from app_cdk.backend.ecs_ec2_cluster_stack import EcsClusterStack
from app_cdk.backend.tg_stack import TargetGroupStack
from app_cdk.backend.alb_stack import LoadBalancerStack
from app_cdk.backend.route53_stack import Route53Stack
from app_cdk.backend.image_builder_stack import ImageBuilderStack
from app_cdk.backend.ec2_stack import Ec2InstanceStack
from app_cdk.backend.task_definition_stack import TaskDefStack
from app_cdk.backend.ecs_service_stack import ECSServiceStack

# ECR
EcrStack(app, "EcrStack")
# Cluster
cluster = EcsClusterStack(app, "EcsClusterStack",env=Environment(account="713767909258", region="eu-north-1"))
# BackendTargetGroup
backend_tg = TargetGroupStack(app, "BackendTargetGroupStack",env=Environment(account="713767909258", region="eu-north-1"))
# ALB
alb = LoadBalancerStack(app, "LoadBalancerStack",env=Environment(account="713767909258", region="eu-north-1"))
# Route 53
Route53Stack(app,"Route53Stack")
# DB Image
ImageBuilderStack(app,"ImageBuilderStack")
# DB instance
ec2 = Ec2InstanceStack(app, "DbEc2InstanceStack",env=Environment(account="713767909258", region="eu-north-1"))
# Backend Task Definition
td = ecs_task_def = TaskDefStack(app, "BackendTaskDefStack")
# Backend Service
ecs_service = ECSServiceStack(app, "ECSServiceStack",{"backend":td.td_map["backend"]},env=Environment(account="713767909258", region="eu-north-1"))

app.synth()

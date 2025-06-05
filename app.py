#!/usr/bin/env python3


import aws_cdk as cdk


from app_cdk.frontend.vpc_stack import VpcStack
from app_cdk.frontend.sg_stack import SecurityStack
from app_cdk.frontend.s3_stack import S3Stack
from app_cdk.frontend.cloudfront_stack import CdnStack
from app_cdk.frontend.frontend_codecommit_stack import CodeCommitFrontendStack
from app_cdk.frontend.frontend_codebuild_stack import CodeBuildFrontendStack
from app_cdk.frontend.frontend_pipeline_stack import PipelineFrontendStack
from app_cdk.frontend.lambda_cdn_invalidator_stack import LambdaCdnInvalidationStack
from app_cdk.frontend.s3_notification_stack import S3NotificationsStack



app = cdk.App()
# VPC
task_vpc = VpcStack(app, "VpcStack")
# SG
sg = SecurityStack(app, "SecurityStack", task_vpc.vpc)
# S3
s3 = S3Stack(app, "S3Stack")
# CDN
cdn = CdnStack(app, "CdnStack",s3.front_bucket)
# CodeCommit
frontend_repo = CodeCommitFrontendStack(app, "CodeCommitFrontendStack")
# CodeBuild
frontend_project = CodeBuildFrontendStack(app,"CodeBuildFrontendStack",repo=frontend_repo.repo,)
# CodePipeline
frontend_pipeline = PipelineFrontendStack(app,"PipelineFrontendStack",repo=frontend_repo.repo,build_project=frontend_project.project,artifact_bucket=s3.frontend_artifact_bucket)
# Lambda
distribution_id = "E2IM6U84VQ7DPI"
lambda_cdn_invalidatior = LambdaCdnInvalidationStack(app, "LambdaCdnInvalidationStack",distribution_id)
# lambda_cdn_invalidatior.add_dependency(s3)
s3not = S3NotificationsStack(app, "S3NotificationsStack", bucket=s3.front_bucket, lambda_fn=lambda_cdn_invalidatior.invalidation_lambda)
s3not.add_dependency(s3)
s3not.add_dependency(lambda_cdn_invalidatior)

# BACKEND

from app_cdk.backend.backend_codecommit_stack import CodeCommitBackendStack
from app_cdk.backend.backend_ecr_stack import EcrStack
from app_cdk.backend.backend_codebuild_stack import CodeBuildBackendStack
from app_cdk.backend.ecs_ec2_cluster_stack import EcsClusterStack
from app_cdk.backend.backend_taskdefinition_stack import BackendTaskDefStack
from app_cdk.backend.alb_stack import LoadBalancerStack
from app_cdk.backend.backend_service_stack import BackendServiceStack
from app_cdk.backend.db_taskdefinition_stack import DbTaskDefStack
from app_cdk.backend.db_service_stack import DbServiceStack
from app_cdk.backend.backend_pipline_stack import PipelineBackendStack
from app_cdk.backend.backend_target_group_stack import BackendTargetGroupStack
from app_cdk.backend.route53_stack import Route53Stack
from app_cdk.backend.db_ec2_stack import DbEc2InstanceStack
from app_cdk.backend.db_image_builder_stack import ImageBuilderStack
# CodeCommit
backend_repo = CodeCommitBackendStack(app, "CodeCommitBackendStack")

# ECR
EcrStack(app, "EcrStack")

# CodeBuild
backend_project = CodeBuildBackendStack(app,"CodeBuildBackendStack",repo=backend_repo.repo)


# Cluster
cluster = EcsClusterStack(app, "EcsClusterStack", task_vpc.vpc,sg.ecs_ec2_cluster_sg)

# BackendTargetGroup
backend_tg = BackendTargetGroupStack(app, "BackendTargetGroupStack",task_vpc.vpc)



# ALB
alb = LoadBalancerStack(app, "LoadBalancerStack", task_vpc.vpc,backend_tg.backend_target_group,sg.alb_sg)

# Route 53
Route53Stack(app,"Route53Stack",alb.alb,cdn.cloudfront)

# DB Image
ImageBuilderStack(app,"ImageBuilderStack",task_vpc.vpc)

# DB instance
db_ec2 = DbEc2InstanceStack(app, "DbEc2InstanceStack",task_vpc.vpc,sg.db_sg)
# Backend Task Definition
backend_task_def = BackendTaskDefStack(app, "BackendTaskDefStack")

# Backend Service
backend_service = BackendServiceStack(app, "BackendServiceStack", cluster.ecs_cluster, backend_task_def.task_def, backend_tg.backend_target_group)
# backend_service.add_dependency(db)
# Backend Pipline
backend_pipeline = PipelineBackendStack(app,"PipelineBackendStack",repo=backend_repo.repo,build_project=backend_project.project,artifact_bucket=s3.backend_artifact_bucket, cluster_name=cluster.cluster_name, service_name=backend_service.service_name,vpc=task_vpc.vpc)

app.synth()

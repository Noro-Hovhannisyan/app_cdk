import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_s3 as s3,
    aws_ecs as ecs,
    aws_ec2 as ec2,
    Aws
)

from constructs import Construct

class PipelineStack(Stack):
    def __init__(self,scope: Construct,construct_id: str,**kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        acc_id = Aws.ACCOUNT_ID
        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent / "configs" / "pipeline.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        for pipeline_conf in config["pipelines"]:
            artifact_bucket = s3.Bucket.from_bucket_name(
                self,pipeline_conf["name"]+"artifact",pipeline_conf["bucket_name"]+"-"+acc_id
            )
            source_output = codepipeline.Artifact()
            build_output = codepipeline.Artifact()
            pipeline = codepipeline.Pipeline(self,pipeline_conf["name"],
                                             artifact_bucket=artifact_bucket
                                             )
            for stage_conf in pipeline_conf["stages"]:
                if stage_conf["name"]=="Source":
                    repo = codecommit.Repository.from_repository_name(
                        self, stage_conf["repo_name"] + "repo", stage_conf["repo_name"]
                    )
                    pipeline.add_stage(
                        stage_name=stage_conf["name"],
                        actions=[
                            cpactions.CodeCommitSourceAction(
                                action_name=stage_conf["action_name"],
                                repository=repo,
                                branch=stage_conf["branch"],
                                output=source_output,
                            )
                        ]
                    )
                if stage_conf["name"]=="Build":
                    project = codebuild.Project.from_project_name(self, pipeline_conf["name"]+"build", stage_conf["project_name"])
                    pipeline.add_stage(
                        stage_name=stage_conf["name"],
                        actions=[
                            cpactions.CodeBuildAction(
                                action_name=stage_conf["action_name"],
                                project=project,
                                input=source_output,
                                outputs=[build_output],
                            )
                        ]
                    )
                if stage_conf["name"]=="Deploy":
                    pipeline.add_stage(
                        stage_name=stage_conf["name"],
                        actions=[
                            cpactions.EcsDeployAction(
                                action_name=stage_conf["action_name"],
                                service=ecs.Ec2Service.from_ec2_service_attributes(
                                    self,
                                    pipeline_conf["name"]+"ECSEC2Service",
                                    service_name=stage_conf["service_name"],
                                    cluster=ecs.Cluster.from_cluster_attributes(
                                        self,
                                        pipeline_conf["name"]+"ECSCluster",
                                        cluster_name=stage_conf["cluster_name"],
                                        vpc=ec2.Vpc.from_lookup(
                                            self,
                                            pipeline_conf["name"]+"VPC",
                                            tags={"Name": stage_conf["vpc_name"]},
                                        )

                                        )
                                    ),
                                input=build_output,
                                )
                        ]
                    )



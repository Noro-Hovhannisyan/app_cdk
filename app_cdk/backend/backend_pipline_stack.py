from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_s3 as s3,
    aws_ecs as ecs,
)
from constructs import Construct

class PipelineBackendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repo: codecommit.IRepository,
        build_project: codebuild.IProject,
        artifact_bucket: s3.IBucket,
        cluster_name: str,
        service_name: str,
        vpc,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_output = codepipeline.Artifact()
        build_output = codepipeline.Artifact()

        self.pipeline = codepipeline.Pipeline(
            self,
            "BackendPipeline",
            artifact_bucket=artifact_bucket
        )

        self.pipeline.add_stage(
            stage_name="Source",
            actions=[
                cpactions.CodeCommitSourceAction(
                    action_name="CodeCommit_Source",
                    repository=repo,
                    branch="master",
                    output=source_output,
                )
            ]
        )

        self.pipeline.add_stage(
            stage_name="Build",
            actions=[
                cpactions.CodeBuildAction(
                    action_name="Build_Backend",
                    project=build_project,
                    input=source_output,
                    outputs=[build_output],

                )
            ]
        )

        self.pipeline.add_stage(
            stage_name="Deploy",
            actions=[
                cpactions.EcsDeployAction(
                    action_name="DeployToEC2ECS",
                    service=ecs.Ec2Service.from_ec2_service_attributes(
                        self,
                        "ECSEC2Service",
                        service_name=service_name,
                        cluster=ecs.Cluster.from_cluster_attributes(
                            self,
                            "ECSCluster",
                            cluster_name=cluster_name,
                            vpc=vpc,
                        )
                    ),
                    input=build_output
                  )
            ]
        )
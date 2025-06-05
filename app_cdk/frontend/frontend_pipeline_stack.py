from aws_cdk import (
    Stack,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as cpactions,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_s3 as s3,
)
from constructs import Construct

class PipelineFrontendStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        repo: codecommit.IRepository,
        build_project: codebuild.IProject,
        artifact_bucket: s3.IBucket,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_output = codepipeline.Artifact()

        self.pipeline = codepipeline.Pipeline(
            self,
            "FrontendPipeline",
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
                    action_name="Build_Frontend",
                    project=build_project,
                    input=source_output,
                )
            ]
        )



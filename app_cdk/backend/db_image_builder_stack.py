from aws_cdk import (
    Stack,
    aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    aws_ec2 as ec2,
    Environment
)
from constructs import Construct



class ImageBuilderStack(Stack):
    def __init__(self, scope: Construct, construc_id: str, vpc, **kwargs):
        super().__init__(scope, construc_id, **kwargs)


        # Role for Image Builder
        instance_role = iam.Role(
            self, "ImageBuilderInstanceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore")
            ]
        )
        instance_role.add_managed_policy(
    iam.ManagedPolicy.from_aws_managed_policy_name("EC2InstanceProfileForImageBuilder")
)

        instance_profile = iam.CfnInstanceProfile(
            self, "ImageBuilderInstanceProfile",
            roles=[instance_role.role_name]
        )

        component = imagebuilder.CfnComponent(
            self, "InstallPostgres14AndInitDB",
            name="InstallPostgres14AndInitDB",
            platform="Linux",
            version="1.0.0",
            data=open("app_cdk/backend/install_postgres.yml").read(),
            uri=None
        )



        # Image recipe
        image_recipe = imagebuilder.CfnImageRecipe(
            self, "PostgresImageRecipe",
            name="PostgresImageRecipe",
            version=f"1.0.0",
            # parent_image="ami-04f6b953f2c230568",
            parent_image="arn:aws:imagebuilder:eu-north-1:aws:image/amazon-linux-2-x86/x.x.x",
            components=[{"componentArn": component.attr_arn}],
        )

        # # Security Group
        # default_sg = ec2.SecurityGroup.from_security_group_id(
        #     self, "DefaultSG",
        #     security_group_id=vpc.vpc_default_security_group
        # )
        # Infrastructure configuration
        infrastructure = imagebuilder.CfnInfrastructureConfiguration(
            self, "PostgresInfraConfig",
            name="PostgresInfraConfig",
            instance_types=["t3.micro"],
            instance_profile_name=instance_profile.ref,
            subnet_id="subnet-0f4f0d0fd980a4eec",
            security_group_ids=["sg-0604964fccb42806f"],
            terminate_instance_on_failure=True
        )


        # Image Pipeline
        image_pipeline = imagebuilder.CfnImagePipeline(
            self, "PostgresImagePipeline",
            name="PostgresImagePipeline",
            image_recipe_arn=image_recipe.attr_arn,
            infrastructure_configuration_arn=infrastructure.attr_arn,
            status="ENABLED",
            schedule=imagebuilder.CfnImagePipeline.ScheduleProperty(
                pipeline_execution_start_condition="EXPRESSION_MATCH_AND_DEPENDENCY_UPDATES_AVAILABLE",
                schedule_expression="cron(0 0 1 1 ? 2099)",
            )
        )


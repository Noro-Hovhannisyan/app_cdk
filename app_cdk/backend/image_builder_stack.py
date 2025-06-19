import yaml
from pathlib import Path
from aws_cdk import (
    Stack,
    aws_imagebuilder as imagebuilder,
    aws_iam as iam,
    aws_ec2 as ec2,
    Environment
)
from constructs import Construct



class ImageBuilderStack(Stack):
    def __init__(self, scope: Construct, construc_id: str, **kwargs):
        super().__init__(scope, construc_id, **kwargs)

        # --- Loading configs ---
        config_path = Path(__file__).resolve().parent.parent / "configs" / "image_builder.yaml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        for builder_conf in config["builders"]:

            # Role for Image Builder
            instance_role = iam.Role(
                self, builder_conf["name"]+"role",
                assumed_by=iam.ServicePrincipal(builder_conf["assumed_by"]),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(builder_conf["managed_policies"]),
                ]
            )
            instance_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name(builder_conf["managed_policy_name"])
            )

            instance_profile = iam.CfnInstanceProfile(
                self, builder_conf["name"]+"profile",
                roles=[instance_role.role_name]
            )

            component = imagebuilder.CfnComponent(
                self, builder_conf["component_name"],
                name=builder_conf["name"],
                platform=builder_conf["platform"],
                version=builder_conf["component_version"],
                data=open(builder_conf["data"]).read() if builder_conf.get("data") else None,
            )
                   # Image recipe
            image_recipe = imagebuilder.CfnImageRecipe(
                self, builder_conf["recipe_name"],
                name=builder_conf["recipe_name"],
                version=f"{builder_conf['recipe_version']}",
                parent_image=builder_conf["parent_image"],
                components=[{"componentArn": component.attr_arn}],
            )

            # Infrastructure configuration
            infrastructure = imagebuilder.CfnInfrastructureConfiguration(
                self, builder_conf["infra_name"],
                name=builder_conf["infra_name"],
                instance_types=builder_conf["instance_types"],
                instance_profile_name=instance_profile.ref,
                subnet_id=builder_conf["subnet_id"],
                security_group_ids=builder_conf["security_group_ids"],
                terminate_instance_on_failure=builder_conf["terminate_instance_on_failure"],
            )


            # Image Pipeline
            image_pipeline = imagebuilder.CfnImagePipeline(
                self, builder_conf["pipeline_name"],
                name=builder_conf["pipeline_name"],
                image_recipe_arn=image_recipe.attr_arn,
                infrastructure_configuration_arn=infrastructure.attr_arn,
                status=builder_conf["status"],
                schedule=imagebuilder.CfnImagePipeline.ScheduleProperty(
                    pipeline_execution_start_condition=builder_conf["pipeline_execution_start_condition"],
                    schedule_expression=builder_conf["schedule_expression"],
                )
            )
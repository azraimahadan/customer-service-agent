from aws_cdk import (
    Stack,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    aws_s3 as s3,
    RemovalPolicy
)
from constructs import Construct

class CICDStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for pipeline artifacts
        artifacts_bucket = s3.Bucket(
            self, "PipelineArtifacts",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # CodeBuild project
        build_project = codebuild.Project(
            self, "BuildProject",
            source=codebuild.Source.git_hub(
                owner="YOUR_GITHUB_USERNAME",  # Replace with your GitHub username
                repo="YOUR_REPO_NAME",         # Replace with your repo name
                webhook=True,
                webhook_filters=[
                    codebuild.FilterGroup.in_event_of(
                        codebuild.EventAction.PUSH
                    ).and_branch_is("main")
                ]
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=True
            ),
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml")
        )

        # Add necessary permissions to CodeBuild
        build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "cloudformation:*",
                    "s3:*",
                    "lambda:*",
                    "apigateway:*",
                    "iam:*",
                    "rekognition:*",
                    "bedrock:*",
                    "polly:*",
                    "transcribe:*",
                    "logs:*"
                ],
                resources=["*"]
            )
        )

        # Source artifact
        source_output = codepipeline.Artifact()

        # CodePipeline
        pipeline = codepipeline.Pipeline(
            self, "DeploymentPipeline",
            artifact_bucket=artifacts_bucket,
            stages=[
                codepipeline.StageProps(
                    stage_name="Source",
                    actions=[
                        codepipeline_actions.GitHubSourceAction(
                            action_name="GitHub_Source",
                            owner="YOUR_GITHUB_USERNAME",  # Replace with your GitHub username
                            repo="YOUR_REPO_NAME",         # Replace with your repo name
                            branch="main",
                            oauth_token=self.node.try_get_context("github_token"),
                            output=source_output
                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name="Build",
                    actions=[
                        codepipeline_actions.CodeBuildAction(
                            action_name="Build",
                            project=build_project,
                            input=source_output
                        )
                    ]
                )
            ]
        )
from aws_cdk import (
    Stack,
    aws_rekognition as rekognition,
    aws_s3 as s3,
    CfnOutput
)
from constructs import Construct

class MLStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, storage_bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Rekognition Custom Labels project (placeholder - requires manual training)
        self.rekognition_project = rekognition.CfnProject(
            self, "RouterDetectionProject",
            project_name="unifi-router-detection"
        )
        
        self.rekognition_project_arn = self.rekognition_project.attr_arn

        # Bedrock Agent (placeholder - requires manual configuration)
        # Note: Bedrock agents are typically created via console or CLI
        # This is a placeholder for the agent ID that will be created manually
        self.bedrock_agent_id = "PLACEHOLDER_AGENT_ID"
        
        # Output the Rekognition project ARN for reference
        CfnOutput(
            self, "RekognitionProjectArn",
            value=self.rekognition_project_arn,
            description="ARN of the Rekognition Custom Labels project"
        )
        
        CfnOutput(
            self, "BedrockAgentId",
            value=self.bedrock_agent_id,
            description="Bedrock Agent ID (to be configured manually)"
        )
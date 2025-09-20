from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class WebStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, api_url: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for static web hosting
        web_bucket = s3.Bucket(
            self, "WebBucket",
            bucket_name=f"customer-service-web-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "WebDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(web_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            default_root_object="index.html"
        )

        # Deploy web assets
        s3deploy.BucketDeployment(
            self, "WebDeployment",
            sources=[s3deploy.Source.asset("web_client/build")],
            destination_bucket=web_bucket,
            distribution=distribution,
            distribution_paths=["/*"]
        )

        # Output web URL
        CfnOutput(
            self, "WebUrl",
            value=f"https://{distribution.distribution_domain_name}",
            description="Web client URL"
        )
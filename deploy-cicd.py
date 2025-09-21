#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.cicd_stack import CICDStack

app = cdk.App()

# Deploy CI/CD pipeline
cicd_stack = CICDStack(app, "CustomerServiceCICD")

app.synth()
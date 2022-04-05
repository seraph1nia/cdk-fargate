#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.fargatestack import FargateStack

app = cdk.App()

fargatestack = FargateStack(app, "FargateStack")

app.synth()
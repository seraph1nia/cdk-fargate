#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import Tags
from stacks.fargatestack import FargateStack


env = "test"

app = cdk.App()

fargatestack = FargateStack(app, f"{env}-FargateStack", tags= {
    'cdk': 'true'
})

# tag all resources met env
# https://docs.aws.amazon.com/cdk/v2/guide/tagging.html
Tags.of(fargatestack).add("environment", env)
Tags.of(fargatestack).add("stackname", fargatestack.stack_name)
Tags.of(fargatestack).add("deployed_by", fargatestack.account)


app.synth()
#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import Tags, Stack
from fargatestack import FargateStack


env = "test4"

app = cdk.App()



fargatestack = FargateStack(app, f"{env}-FargateStack", tags= {
    'cdk': 'true',
    
},)

# monitoringstack = MonitoringStack(app, f"{env}-MonitoringStack", fargatestack=fargatestack)

# tag all resources met env
# https://docs.aws.amazon.com/cdk/v2/guide/tagging.html
Tags.of(fargatestack).add("environment", env)
Tags.of(fargatestack).add("stackname", fargatestack.stack_name)
# hoe krijg je de identity?
# Tags.of(fargatestack).add("deployed_by", Stack.of(fargatestack).)


app.synth()
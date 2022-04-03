import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_fargate.cdk_fargate_stack import CdkFargateStack

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_fargate/cdk_fargate_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CdkFargateStack(app, "cdk-fargate")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

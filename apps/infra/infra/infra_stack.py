from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    Duration,
)
from aws_cdk.aws_ecr import Repository
from constructs import Construct

class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        repository = Repository(self, "RepoNaampje")        
        repository.add_lifecycle_rule(max_image_age=Duration.days(30))
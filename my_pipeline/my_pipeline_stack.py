import aws_cdk as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from constructs import Construct
from os import path
from aws_cdk.aws_ecr_assets import DockerImageAsset, NetworkMode

import aws_cdk.aws_codebuild as codebuild

class MyPipelineStack(cdk.Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)


        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecr_assets/DockerImageAsset.html
        asset = DockerImageAsset(self, "MyBuildImage",
            directory=path.join("./my_pipeline"),
            network_mode=NetworkMode.HOST
        )

        
        source = CodePipelineSource.git_hub("seraph1nia/cdk-fargate", "main")
        
        synth = ShellStep("Synth", 
                            input=source,
                            commands=["npm install -g aws-cdk", 
                                "python -m pip install -r requirements.txt",
                                "aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin https://911420038161.dkr.ecr.eu-central-1.amazonaws.com",
                                "cdk synth"]
                        )
        
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.pipelines/CodePipeline.html
        pipeline =  CodePipeline(self, "Pipeline", 
                        pipeline_name="MyPipeline",
                        synth=synth
                    )
        
        
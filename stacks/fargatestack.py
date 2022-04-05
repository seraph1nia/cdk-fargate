from aws_cdk import Stack
import aws_cdk.aws_ec2 as ec2
from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_ecs as ecs,
)
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
)
import pathlib
from constructs import Construct

from os import path


containerport=8080


class FargateStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # VPC
        self.vpc = ec2.Vpc(self, "VPC-CDK",
                           max_azs=3,
                           cidr="10.42.0.0/16",
                           subnet_configuration=[ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PUBLIC,
                               name="Public",
                               cidr_mask=24
                           ), ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                               name="Private",
                               cidr_mask=24
                           )
                           ],
                           nat_gateways=1,
                           )
        
        # ecs cluster 
        self.cluster = ecs.Cluster(
            self, 'EcsCluster',
            vpc=self.vpc
        )
        

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs_patterns/NetworkLoadBalancedFargateService.html
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=self.cluster,                
            task_image_options={
                'image': ecs.ContainerImage.from_asset("stacks"),
                'container_port': 8080,
                'container_name': 'nginx'
                
            },
        )
        
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            # dit is de fargateproxy
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )
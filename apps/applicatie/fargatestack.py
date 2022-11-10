import aws_cdk.aws_ec2 as ec2
from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    CfnOutput,
    aws_codebuild,
    aws_codepipeline,
)
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_s3 as s3,
    aws_s3_assets,
    aws_elasticloadbalancingv2 as elbv2,
    App, CfnOutput, Duration, Stack
)
import pathlib
from constructs import Construct


from aws_cdk.aws_certificatemanager import Certificate
from aws_cdk.aws_elasticloadbalancingv2 import SslPolicy


from os import path



class FargateStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        frontendport = 5000
        redisport = 6379
        self.redispassword = "jemoeder" # TODO: aws secrets manager/ parameter store met sops icm kms en yaml loopje script

        ###
        ### VPC
        ###
        self.vpc = ec2.Vpc(self, "VPC-CDK",
                           max_azs=3,
                           cidr="10.43.0.0/16",
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
        
        ###
        ### ECS
        ###
        self.cluster = ecs.Cluster(
            self, 'EcsCluster',
            vpc=self.vpc
        )
        

        ###
        ### Redis Backend
        ###
        

        self.fargate_backend = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "Backend",
            
            memory_limit_mib=512,
            desired_count=2,
            cpu=256,
            listener_port=redisport,
            cluster=self.cluster,                
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image = ecs.ContainerImage.from_registry("bitnami/redis:7.0.5"),
                container_port = redisport,
                container_name = "redis",
                environment = {
                    "REDIS_PASSWORD": self.redispassword
                }                
        ),
            public_load_balancer = False,            # in welk subnet komt dit dan?
            task_subnets=ec2.SubnetSelection(subnets=self.vpc.private_subnets) # is dit voor de tasks of ook alb?
            
        )
        self.fargate_backend.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            # dit is de fargateproxy
            connection = ec2.Port.tcp(redisport),
            description="Allow http inbound from VPC"
        )
        scalable_target = self.fargate_backend.service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=3
        )
        
        scalable_target.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=50
        )
        
        scalable_target.scale_on_memory_utilization("MemoryScaling",
            target_utilization_percent=50
        )

        ###
        ### FLASK FRONTEND
        ###

        # waar prop je dit in?
        health_check = elbv2.HealthCheck( 
            interval=Duration.seconds(60),
            path="/health",
            timeout=Duration.seconds(5)
        )

        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedFargateService.html
        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "Frontend",
            memory_limit_mib=512,
            desired_count=2,
            cpu=256,
            cluster=self.cluster,                
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image = ecs.ContainerImage.from_asset("src/frontend"),
                container_port = frontendport,
                container_name = 'flask',
                # dit soort dingen op een andere manier doen, parameter store?, hoe krijg je het dan de parameter store in?
                environment = {
                    "REDIS_PASSWORD": self.redispassword,
                    "REDIS_URL": self.fargate_backend.load_balancer.load_balancer_dns_name,
                } 
                
            ),
            
              
            public_load_balancer = True,            # in welk subnet komt dit dan?
            task_subnets=ec2.SubnetSelection(subnets=self.vpc.private_subnets) # is dit voor de tasks of ook alb?
        )
        
        self.fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            # dit is de fargateproxy
            connection = ec2.Port.tcp(frontendport),
            description="Allow http inbound from VPC"
        )
        self.fargate_service.target_group.health_check
        # Autoscaling shit
            
        
        scalable_target = self.fargate_service.service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=3
        )
        
        scalable_target.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=50
        )
        
        scalable_target.scale_on_memory_utilization("MemoryScaling",
            target_utilization_percent=50
        )
     
        # print public DNS
        CfnOutput(self,"public dns",value=self.fargate_service.load_balancer.load_balancer_dns_name)
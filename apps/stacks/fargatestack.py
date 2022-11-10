from aws_cdk import Stack
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
)
import pathlib
from constructs import Construct


from aws_cdk.aws_certificatemanager import Certificate
from aws_cdk.aws_elasticloadbalancingv2 import SslPolicy


from os import path



class FargateStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # self.repository = Repository(self, "Repository")

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
        

        # my_hosted_zone = route53.HostedZone(self, "HostedZone",
        #     zone_name="example.com"
        # )
        # my_cert = acm.Certificate(self, "Certificate",
        #     domain_name="hello.example.com",
        #     validation=acm.CertificateValidation.from_dns(my_hosted_zone)
        # )


        # misschien in een andere stack?
        bucket = s3.Bucket(self, "MyBucket")
        # dockerfile naar s3.
        
        # container build shit
        # codebuildsource = aws_codebuild.Source.s3(bucket=
        # path: builtins.str,

        # pipeline = codepipeline.Pipeline(self, "MyFirstPipeline",
        #     pipeline_name="MyPipeline"
        # )
        
        
        
        # ecr_source_variables = codepipeline_actions.EcrSourceVariables(
        #     image_digest="imageDigest",
        #     image_tag="imageTag",
        #     image_uri="imageUri",
        #     registry_id="registryId",
        #     repository_name="repositoryName"
        # )        
        


        source_output = codepipeline.Artifact() # waar is de data?
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build1",
            input=source_output,
            project=codebuild.PipelineProject(self, "Project",
                # wat doe je met de data?
                build_spec=codebuild.BuildSpec.from_object({
                    "version": "0.2",
                    "env": {
                        "exported-variables": ["MY_VAR"
                        ]
                    },
                    "phases": {
                        "build": {
                            "commands": 'export MY_VAR="some value"'
                        }
                    }
                })
            ),
            variables_namespace="MyNamespace"
        )


        frontendport = 8080
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedFargateService.html
        self.fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "Frontend",
            memory_limit_mib=512,
            desired_count=2,
            cpu=256,
            cluster=self.cluster,                
            task_image_options={
                'image': ecs.ContainerImage.from_registry("bitnami/nginx:latest"),
                'container_port': frontendport,
                'container_name': 'nginx'
                
            },
            public_load_balancer = True,            # in welk subnet komt dit dan?
            task_subnets=ec2.SubnetSelection(subnets=self.vpc.private_subnets) # is dit voor de tasks of ook alb?
        )
        
        self.fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            # dit is de fargateproxy
            connection = ec2.Port.tcp(frontendport),
            description="Allow http inbound from VPC"
        )

        # Autoscaling shit
            
        
        scalable_target = self.fargate_service.service.auto_scale_task_count(
            min_capacity=1,
            max_capacity=20
        )
        
        scalable_target.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=50
        )
        
        scalable_target.scale_on_memory_utilization("MemoryScaling",
            target_utilization_percent=50
        )




        redisport = 6379
        self.fargate_backend = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "Backend",
            
            
            memory_limit_mib=512,
            desired_count=2,
            cpu=256,
            cluster=self.cluster,                
            task_image_options={
                'image': ecs.ContainerImage.from_registry("bitnami/redis:7.0.5"),
                'container_port': redisport,
                'container_name': 'redis'
                
            },
            public_load_balancer = False,            # in welk subnet komt dit dan?
            task_subnets=ec2.SubnetSelection(subnets=self.vpc.private_subnets) # is dit voor de tasks of ook alb?
        )
        self.fargate_backend.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
            # dit is de fargateproxy
            connection = ec2.Port.tcp(frontendport),
            description="Allow http inbound from VPC"
        )
        
        # # vanuit service zelf
        # self.testmetric = self.fargate_service.service.metric_memory_utilization()
        # self.lbmetric = self.fargate_service.load_balancer.metric_processed_bytes()
        
        # self.fargate_service.target_group.metric_healthy_host_count()
        
        
        

        # print public DNS
        CfnOutput(self,"public dns",value=self.fargate_service.load_balancer.load_balancer_dns_name)
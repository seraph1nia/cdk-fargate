from constructs import Construct
from aws_cdk import Stack
from aws_cdk import aws_cloudwatch as cloudwatch

from stacks import fargatestack


class MonitoringStack(Stack):

    def __init__(self, scope: Construct, id: str, fargatestack, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        

        self.fargatestack = fargatestack




        # dashboard
        self.dashboard = cloudwatch.Dashboard(self, "MyDashboard",
            dashboard_name="dashboardName",
            end="end",
            period_override=cloudwatch.PeriodOverride.AUTO,
            start="start"
        )
        
        
        # Metric
        
        
        memmetric = self.fargatestack.testmetric
        lbmetric = self.fargatestack.lbmetric
        # memmetric = cloudwatch.Metric(
        #     label=f"{self.fargatestack.fargate_service.service.service_name}-mem",
        #     metric_name="MemoryUtilization",
        #     # https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/aws-services-cloudwatch-metrics.html
        #     namespace="AWS/ECS",
        #     dimensions_map={
        #         "ClusterName": self.fargatestack.cluster.cluster_name,
        #         "ServiceName": self.fargatestack.fargate_service.service.service_name
        #     }
        # )   
        
        cpumetric = cloudwatch.Metric(
            label=f"{self.fargatestack.fargate_service.service.service_name}-cpu",
            metric_name="CPUUtilization",
            namespace="AWS/ECS",
            dimensions_map={
                "ClusterName": self.fargatestack.cluster.cluster_name,
                "ServiceName": self.fargatestack.fargate_service.service.service_name
            }
        )
        
        graphmem = cloudwatch.GraphWidget(
            width = 24,
            title =  'graphmem',
            left = [memmetric],
        )
        graphcpu = cloudwatch.GraphWidget(
            width = 24,
            title =  'graphcpu',
            left = [cpumetric],
        )
        graphlb = cloudwatch.GraphWidget(
            width = 24,
            title =  'graphlb',
            left = [lbmetric],
        )

        self.dashboard.add_widgets(graphmem)
        self.dashboard.add_widgets(graphcpu)
        self.dashboard.add_widgets(graphlb)
            
        

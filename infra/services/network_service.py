from aws_cdk import (
    aws_ec2,
    Duration,
    Stack,
)
from constructs import Construct
from typing import Dict, List, Tuple
from configs.deployment_config import DeploymentConfig

class NetworkService(Construct):

    def __init__(self, scope: Construct, configs: DeploymentConfig, **kwargs) -> None:
        super().__init__(scope, f"{configs.deployment_name}-network")

        # VPC
        self.vpc = self.__createVPC(configs.deployment_name,
                               configs.app_parameters["vpc"])
        
        # Security Group for Lambda
        self.lambda_sg = aws_ec2.SecurityGroup(
            self,
            f"{configs.deployment_name}-lambda-sg",
            vpc=self.vpc,
            allow_all_outbound=False,
        )
        self.lambda_sg.add_egress_rule(
            aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(443)
        )

        # Security Group for EventBridge
        self.eventbridge_sg = aws_ec2.SecurityGroup(
            self,
            f"{configs.deployment_name}-eventbridge-sg",
            vpc=self.vpc,
            allow_all_outbound=False,
        )
        self.eventbridge_sg.add_egress_rule(
            aws_ec2.Peer.any_ipv4(), aws_ec2.Port.tcp(443)
        )

        self.eventbridge_sg.add_ingress_rule(
            peer=aws_ec2.Peer.security_group_id(self.lambda_sg.security_group_id), 
            connection=aws_ec2.Port.tcp(443),
        )
        
    def __createVPC(self: Construct, deployment_name: str, vpc_configs: Dict) -> aws_ec2.Vpc:
        vpc = aws_ec2.Vpc(self, f'{deployment_name}-vpc',
                          vpc_name=f'{deployment_name}-vpc',
                          ip_addresses=aws_ec2.IpAddresses.cidr(
                              vpc_configs["cidr"]),
                          enable_dns_hostnames=vpc_configs["enable_dns_hostnames"],
                          enable_dns_support=vpc_configs["enable_dns_support"],
                          subnet_configuration=[
                            aws_ec2.SubnetConfiguration(
                                name=f"{deployment_name}-public-subnet",
                                subnet_type=aws_ec2.SubnetType.PUBLIC,
                                cidr_mask=24,
                            ),
                            aws_ec2.SubnetConfiguration(
                                name=f"{deployment_name}-private-subnet",
                                subnet_type=aws_ec2.SubnetType.PRIVATE_WITH_EGRESS,
                                cidr_mask=24,
                            ),
                            aws_ec2.SubnetConfiguration(
                                name=f"{deployment_name}-isolated-subnet",
                                subnet_type=aws_ec2.SubnetType.PRIVATE_ISOLATED,
                                cidr_mask=24,
                            ),
                         ],
                         nat_gateways=1)
        return vpc

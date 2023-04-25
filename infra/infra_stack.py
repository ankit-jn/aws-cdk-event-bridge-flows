from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
)
from constructs import Construct
from typing import Dict, List, Tuple
from configs.deployment_config import DeploymentConfig

from infra.services.network_service import NetworkService
from infra.services.function_service import FunctionService
from infra.services.api_service import ApiService
from infra.services.events_service import EventsService


class InfraStack(Stack):
    def __init__(
        self, scope: Construct, construct_id: str, configs: DeploymentConfig, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        aws_region = configs.app_parameters["aws_region"]

        network_service = NetworkService(scope=self, configs=configs)
        function_service = FunctionService(
            scope=self, configs=configs, network_service=network_service
        )
        api_service = ApiService(
            scope=self, configs=configs, function_service=function_service
        )
        events_service = EventsService(
            scope=self,
            configs=configs,
            network_service=network_service,
            function_service=function_service,
            api_service=api_service,
        )

        CfnOutput(
            self,
            "vpc",
            value=network_service.vpc.vpc_id,
            export_name=f"{configs.deployment_name}-vpc-id",
        )

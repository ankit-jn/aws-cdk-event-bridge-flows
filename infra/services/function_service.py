from aws_cdk import (
    aws_lambda,
    aws_ec2,
    Duration,
    Stack,
)
from constructs import Construct
from configs.deployment_config import DeploymentConfig
from infra.services.network_service import NetworkService

FUNCTIONS_SOURCE_PATH = "./functions"
DEFAULT_LAMBDA_TIMEOUT = Duration.seconds(15)
DEFAULT_LAMBDA_MEMORY_USAGE = 512

class FunctionService(Construct):

    def __init__(self, scope: Construct, configs: DeploymentConfig, network_service: NetworkService, **kwargs) -> None:
        super().__init__(scope, f"{configs.deployment_name}-functions")
        
        stack: Stack = Stack.of(self)
        event_bus_name=configs.app_parameters["event_bus_name"]
        event_bus_Arn = f"arn:aws:events:{stack.region}:{stack.account}:event-bus/{configs.deployment_name}-{event_bus_name}"
        
        # Provision lambda layer
        layer = aws_lambda.LayerVersion(
            self,
            id=f"{configs.deployment_name}-lambda-layer",
            code=aws_lambda.Code.from_asset("./layer"),
            compatible_runtimes=[aws_lambda.Runtime.PYTHON_3_9],
        )

        # Event Generator Lambda
        self.event_generator_lambda = self.__createEventGeneratorLambda(
            configs.deployment_name,
            layer,
            network_service.lambda_sg,
            network_service.vpc,
            event_bus_Arn
        )
        
        # Order Receiver Lambda
        self.order_receiver_lambda = self.__createOrderReceiverLambda(
            configs.deployment_name,
            layer,
            network_service.lambda_sg,
            network_service.vpc
        )
        
        # Order Processor Lambda
        self.order_processor_lambda = self.__createOrderProcessorLambda(
            configs.deployment_name,
            layer,
            network_service.lambda_sg,
            network_service.vpc
        ) 

        # Order Shipment Lambda
        self.event_processor_lambda = self.__createOrderShipmentLambda(
            configs.deployment_name,
            layer,
            network_service.lambda_sg,
            network_service.vpc
        )
    
    def __createEventGeneratorLambda(
            self: Construct,
            deployment_name: str,
            layer: aws_lambda.LayerVersion,
            lambda_sg: aws_ec2.SecurityGroup,
            vpc: aws_ec2.Vpc,
            event_bus_Arn: str
    ) -> aws_lambda.Function:
        
        event_generator_lambda = aws_lambda.Function(
            self,
            id=f"{deployment_name}-event-generator",
            function_name=f"{deployment_name}-event-generator",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset(
                f"{FUNCTIONS_SOURCE_PATH}/event_generator"
            ),
            handler="lambda_function.lambda_handler",
            timeout=DEFAULT_LAMBDA_TIMEOUT,
            memory_size=DEFAULT_LAMBDA_MEMORY_USAGE,
            layers=[layer],
            environment={
                "EVENT_BUS_ARN": event_bus_Arn
            },
            security_groups=[lambda_sg],
            vpc=vpc,
            allow_all_outbound=False,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=vpc.private_subnets),
            tracing=aws_lambda.Tracing.ACTIVE,
        )
        return event_generator_lambda
    
    def __createOrderReceiverLambda(
            self: Construct,
            deployment_name: str,
            layer: aws_lambda.LayerVersion,
            lambda_sg: aws_ec2.SecurityGroup,
            vpc: aws_ec2.Vpc
    ) -> aws_lambda.Function:
        
        order_receiver_lambda = aws_lambda.Function(
            self,
            id=f"{deployment_name}-order-receiver",
            function_name=f"{deployment_name}-order-receiver",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset(
                f"{FUNCTIONS_SOURCE_PATH}/order_receiver"
            ),
            handler="lambda_function.lambda_handler",
            timeout=DEFAULT_LAMBDA_TIMEOUT,
            memory_size=DEFAULT_LAMBDA_MEMORY_USAGE,
            layers=[layer],
            environment={
            },
            security_groups=[lambda_sg],
            vpc=vpc,
            allow_all_outbound=False,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=vpc.private_subnets),
            tracing=aws_lambda.Tracing.ACTIVE,
        )
        return order_receiver_lambda
    
    def __createOrderProcessorLambda(
            self: Construct,
            deployment_name: str,
            layer: aws_lambda.LayerVersion,
            lambda_sg: aws_ec2.SecurityGroup,
            vpc: aws_ec2.Vpc
    ) -> aws_lambda.Function:
        
        order_processor_lambda = aws_lambda.Function(
            self,
            id=f"{deployment_name}-order-processor",
            function_name=f"{deployment_name}-order-processor",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset(
                f"{FUNCTIONS_SOURCE_PATH}/order_processor"
            ),
            handler="lambda_function.lambda_handler",
            timeout=DEFAULT_LAMBDA_TIMEOUT,
            memory_size=DEFAULT_LAMBDA_MEMORY_USAGE,
            layers=[layer],
            environment={
            },
            security_groups=[lambda_sg],
            vpc=vpc,
            allow_all_outbound=False,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=vpc.private_subnets),
            tracing=aws_lambda.Tracing.ACTIVE,
        )
        return order_processor_lambda
    
    def __createOrderShipmentLambda(
            self: Construct,
            deployment_name: str,
            layer: aws_lambda.LayerVersion,
            lambda_sg: aws_ec2.SecurityGroup,
            vpc: aws_ec2.Vpc
    ) -> aws_lambda.Function:
        
        order_shipment_lambda = aws_lambda.Function(
            self,
            id=f"{deployment_name}-order-shipment",
            function_name=f"{deployment_name}-order-shipment",
            runtime=aws_lambda.Runtime.PYTHON_3_9,
            code=aws_lambda.Code.from_asset(
                f"{FUNCTIONS_SOURCE_PATH}/order_shipment"
            ),
            handler="lambda_function.lambda_handler",
            timeout=DEFAULT_LAMBDA_TIMEOUT,
            memory_size=DEFAULT_LAMBDA_MEMORY_USAGE,
            layers=[layer],
            environment={
            },
            security_groups=[lambda_sg],
            vpc=vpc,
            allow_all_outbound=False,
            vpc_subnets=aws_ec2.SubnetSelection(subnets=vpc.private_subnets),
            tracing=aws_lambda.Tracing.ACTIVE,
        )
        return order_shipment_lambda

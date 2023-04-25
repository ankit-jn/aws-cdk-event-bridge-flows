from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_ec2, aws_iam, aws_events
from aws_cdk import aws_logs as logs
from aws_cdk import aws_sqs as sqs
from constructs import Construct
from configs.deployment_config import DeploymentConfig
from infra.services.network_service import NetworkService
from infra.services.function_service import FunctionService
from infra.services.api_service import ApiService

from infra.services.event_rule_cloudwatch import create_event_rule_cloudWatch
from infra.services.event_rule_order_receiver import create_event_rule_order_receiver
from infra.services.event_rule_order_processor import create_event_rule_order_processor
from infra.services.event_rule_order_shipment import create_event_rule_order_shipment
from infra.services.event_rule_order_delivery import create_event_rule_order_delivery

class EventsService(Construct):

    def __init__(
        self,
        scope: Construct,
        configs: DeploymentConfig,
        network_service: NetworkService,
        function_service: FunctionService,
        api_service: ApiService,
        **kwargs,
    ) -> None:
        super().__init__(scope, f"{configs.deployment_name}-events")

        # Cloudwatch Log Group for logging all events
        self.events_log_group = logs.LogGroup(
            self,
            id=f"{configs.deployment_name}-events",
            log_group_name=f"{configs.deployment_name}-events",
            retention=logs.RetentionDays.ONE_YEAR,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # SQS Queue: Dead-Letter Queue
        self.dead_letter_queue = sqs.Queue(
            self,
            id=f"{configs.deployment_name}-dead-letter-queue",
            queue_name=f"{configs.deployment_name}-dead-letter-queue",
            visibility_timeout=Duration.seconds(300),
        )

        # Event Bus
        event_bus_name=configs.app_parameters["event_bus_name"]
        self.event_bus = aws_events.EventBus(
            self,
            id=f"{configs.deployment_name}-{event_bus_name}",
            event_bus_name=f"{configs.deployment_name}-{event_bus_name}",
        )

        network_service.vpc.add_interface_endpoint(
            id=f"{configs.deployment_name}-event-bridge-interface",
            service=aws_ec2.InterfaceVpcEndpointAwsService.EVENTBRIDGE,
            security_groups=[network_service.eventbridge_sg],
        )

        # Event Rule #1 [CloudWatch]: All events with event-type prefix as "order" -> Logged to CloudWatch Log Group
        create_event_rule_cloudWatch(
            self,
            configs.deployment_name,
            self.event_bus,
            self.events_log_group,
            self.dead_letter_queue,
        )

        # Event Rule #2 [order_receive]: Events with event-type as "order_receive" -> Sent to Order Receiver Lambda
        create_event_rule_order_receiver(
            self,
            configs.deployment_name,
            self.event_bus,
            function_service.order_receiver_lambda,
            self.dead_letter_queue,
        )

        # Event Rule #3 [order_process]: Events with event-type as "order_process" -> Sent to Order processor Lambda via SQS Queue
        create_event_rule_order_processor(
            self,
            configs.deployment_name,
            self.event_bus,
            function_service.order_processor_lambda,
            self.dead_letter_queue,
        )

        # Event Rule #4 [order_shipment]: Events with event-type as "order_shipment" -> Sent to Order Shipment Lambda via API G/w
        create_event_rule_order_shipment(
            self,
            configs.deployment_name,
            self.event_bus,
            api_service.api,
            self.dead_letter_queue,
        )

        # Event Rule #5 [order_deliver]: Events with event-type as "order_deliver" -> Sent to Oredr Delivery SQS Queue
        create_event_rule_order_delivery(
            self,
            configs.deployment_name,
            self.event_bus,
            self.dead_letter_queue,
        )

        # Permission granted to Event Generator Lambda for putting events on Event Bus
        function_service.event_generator_lambda.add_to_role_policy(
            aws_iam.PolicyStatement(
                effect=aws_iam.Effect.ALLOW,
                actions=["events:PutEvents"],
                resources=[self.event_bus.event_bus_arn],
            )
        )

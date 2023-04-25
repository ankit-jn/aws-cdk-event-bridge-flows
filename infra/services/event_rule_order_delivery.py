from aws_cdk import Duration
from aws_cdk import aws_events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_sqs as sqs
from constructs import Construct

def create_event_rule_order_delivery(
    scope: Construct,
    deployment_name: str,
    event_bus: aws_events.EventBus,
    dead_letter_queue: sqs.Queue,
) -> None:
    """
    Event Rule #5: All the events with event-type as "order_deliver" 
    """

    # Oredr Delivery SQS Queue
    order_delivery_queue = sqs.Queue(
        scope,
        id=f"{deployment_name}-order-delivery-queue",
        queue_name=f"{deployment_name}-order-delivery-queue",
        visibility_timeout=Duration.seconds(300),
    )

    event_rule = aws_events.Rule(
        scope,
        id=f"{deployment_name}-event-rule-order-deliver",
        rule_name=f"{deployment_name}-event-rule-order-deliver",
        description="Event Rule #5 [order-deliver]",
        event_bus=event_bus,
    )
    # All the events with the current AWS account number
    event_rule.add_event_pattern(
        account=[scope.event_bus.env.account],
        detail_type=aws_events.Match.exact_string(value="order_deliver"),
    )

    event_rule.add_target(
        target=targets.SqsQueue(
            queue=order_delivery_queue,
            retry_attempts=2,
            max_event_age=Duration.minutes(15),
            dead_letter_queue=dead_letter_queue,
        )
    )

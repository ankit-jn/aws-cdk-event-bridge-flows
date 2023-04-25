from aws_cdk import Duration
from aws_cdk import aws_events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_lambda
from aws_cdk import aws_sqs as sqs
from constructs import Construct

def create_event_rule_order_receiver(
    scope: Construct,
    deployment_name: str,
    event_bus: aws_events.EventBus,
    order_receiver_lambda: aws_lambda.Function,
    dead_letter_queue: sqs.Queue,
):
    """
    Event Rule #2: All the events with event-type as "order_receive" 
    """
    event_rule = aws_events.Rule(
        scope,
        id=f"{deployment_name}-event-rule-order-receiver",
        rule_name=f"{deployment_name}-event-rule-order-receiver",
        description="Event Rule #2 [order-receiver]",
        event_bus=event_bus,
    )

    # All the events with event-type as "order_receive" 
    event_rule.add_event_pattern(
        account=[event_bus.env.account],
        detail_type=aws_events.Match.exact_string(value="order_receive"),
    )

    # Input Transformer
    order_receiver_input_transformer = {
        "event_type": aws_events.EventField.from_path("$.detail-type"),
        "order_id": aws_events.EventField.from_path( "$.detail.order_id"),
        "payload": {
            "order_id": aws_events.EventField.from_path("$.detail.order_id"),
            "order_date": aws_events.EventField.from_path("$.detail.order_date"),
        },
    }
    event_rule.add_target(
        target=targets.LambdaFunction(
            handler=order_receiver_lambda,
            max_event_age=Duration.hours(2),
            retry_attempts=2,
            dead_letter_queue=dead_letter_queue,
            event=aws_events.RuleTargetInput.from_object(
                order_receiver_input_transformer
            ),
        ),
    )

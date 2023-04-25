from aws_cdk import Duration
from aws_cdk import aws_apigateway, aws_events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_sqs as sqs
from constructs import Construct

def create_event_rule_order_shipment(
    scope: Construct,
    deployment_name: str,
    event_bus: aws_events.EventBus,    
    api: aws_apigateway.RestApi,
    dead_letter_queue: sqs.Queue, 
) -> None:
    """
    Event Rule #4: All the events with event-type as "order_shipment" 
    """

    event_rule = aws_events.Rule(
        scope,
        id=f"{deployment_name}-event-rule-order-shipment",
        rule_name=f"{deployment_name}-event-rule-order-shipment",
        description="Event Rule #3 [order-shipment]",
        event_bus=event_bus,
    )

    # All the events with event-type as "order_process"
    event_rule.add_event_pattern(
        account=[event_bus.env.account],
        detail_type=aws_events.Match.exact_string(value="order_shipment"),
    )

    # Input Transformer
    order_shipment_input_transformer = {
        "event_type": aws_events.EventField.from_path("$.detail-type"),
        "order_id": aws_events.EventField.from_path( "$.detail.order_id"),
        "payload": {
            "order_id": aws_events.EventField.from_path("$.detail.order_id"),
            "order_date": aws_events.EventField.from_path("$.detail.order_date"),
        },
    }
    
    event_rule.add_target(
        target=targets.ApiGateway(
            rest_api=api,
            stage=api.deployment_stage.stage_name,
            method="POST",
            path="/events/shipment",
            post_body=aws_events.RuleTargetInput.from_object(
                order_shipment_input_transformer
            ),
            max_event_age=Duration.hours(2),
            retry_attempts=2,
            dead_letter_queue=dead_letter_queue,
        ),
    )